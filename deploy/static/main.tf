variable "cloudflare_zone" {}
variable "static_domain_name" {}

resource "aws_s3_bucket" "static" {
  bucket = "${var.static_domain_name}"
  force_destroy = true
}

resource "cloudflare_record" "static" {
  zone_id = "${var.cloudflare_zone}"
  name = "${var.static_domain_name}"
  value = "${aws_s3_bucket.static.bucket_regional_domain_name}"
  type = "CNAME"
  ttl = 1
  proxied = true
}

# api redirects
resource "cloudflare_worker_route" "cf_route_static" {
  zone_id = "${var.cloudflare_zone}"
  pattern = "${var.static_domain_name}/*"
  script_name = "${cloudflare_worker_script.cf_script_static.name}"
}

# cache all the things
resource "cloudflare_worker_script" "cf_script_static" {
  name = "api_redirects_static"
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
  return fetch(request, { cf: { cacheEverything: true } })
}
EOF
}

# file uploads
resource "null_resource" "upload_to_s3" {
  triggers = {
    always = "${uuid()}" # always run, aws s3 sync will take care of only modified files etc 
  }

  provisioner "local-exec" {
    command = "aws s3 sync --acl public-read ${path.module}/../../static s3://${aws_s3_bucket.static.id}"
  }
}


