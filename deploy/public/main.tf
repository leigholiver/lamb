# this file is managed by lamb, any changes to it will be lost
# edit 'main.tf.j2' and run'./lambctl make terraform' to regenerate it

variable "cloudflare_zone" {}
variable "domain_name" {}

resource "aws_s3_bucket" "public" {
  bucket = "www.${var.domain_name}"
  force_destroy = true
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "cloudflare_record" "public" {
  zone_id = "${var.cloudflare_zone}"
  name = "${var.domain_name}"
  value = "${aws_s3_bucket.public.website_domain}"
  type = "CNAME"
  ttl = 1
  proxied = true
}

resource "cloudflare_record" "public_www" {
  zone_id = "${var.cloudflare_zone}"
  name = "www.${var.domain_name}"
  value = "${var.domain_name}"
  type = "CNAME"
  ttl = 1
  proxied = true
}

resource "null_resource" "upload_to_s3_public" {
  triggers = {
    always = "${uuid()}" # always run, aws s3 sync will take care of only modified files etc 
  }

  provisioner "local-exec" {
    command = "aws s3 sync --delete --acl public-read ${path.module}/../../public s3://${aws_s3_bucket.public.id}"
  }
}

# force https
resource "cloudflare_worker_route" "cf_route_https" {
  zone_id = "${var.cloudflare_zone}"
  pattern = "www.${var.domain_name}/*"
  script_name = "${cloudflare_worker_script.cf_script_https.name}"
}

# cf worker to force https so you dont use all 3 free page rules
resource "cloudflare_worker_script" "cf_script_https" {
  name = "https_redirects"
  content = <<EOF
addEventListener('fetch', event => {
  event.respondWith(bulkRedirects(event.request))
})

async function bulkRedirects(request) {
    // force https
    if(request.url.startsWith("http://")) {
      loc = request.url.replace("http://", "https://")
      return Response.redirect(loc, 307) 
    }
  return fetch(request)
}
EOF
}

# redirect www to non www
resource "cloudflare_worker_route" "cf_route_www" {
  zone_id = "${var.cloudflare_zone}"
  pattern = "${var.domain_name}/*"
  script_name = "${cloudflare_worker_script.cf_script_www.name}"
}

resource "cloudflare_worker_script" "cf_script_www" {
  name = "www_redirects"
  content = <<EOF
addEventListener('fetch', event => {
  event.respondWith(bulkRedirects(event.request))
})

async function bulkRedirects(request) {
    // force https
    if(request.url.startsWith("http://")) {
      loc = request.url.replace("http://", "https://")
      return Response.redirect(loc, 307) 
    }

    // redirect www to non www based on domain name
    if(request.url.startsWith("https://${var.domain_name}")) {
      loc = request.url.replace("https://${var.domain_name}", "https://www.${var.domain_name}")
      return Response.redirect(loc, 307) 
    }
  return fetch(request)
}
EOF
}