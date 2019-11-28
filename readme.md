### lamb

super simple python framework for aws api gateway/lambda/dynamodb/s3

this is a weekend hobby project it is probably not wise to use



#### routes:

routes are defined in `routes.py`. after modifying this file you will need to run `./lambctl make routes` to compile them

```
routes = [
    "/test/(id)": {                   # the path for the route
        "methods": [ "GET", "POST" ], # one or more of any method supported by lambda/api gateway
        "action": "default.ping",     # controller function, in the format class.function
        "middleware": [               # array of middleware to run before the request hits the controller
        	"test"
        ]
    },
]

```



#### controllers:
`./lambctl make controller [name]`

a controller contains one or many route functions, which accept an `event` parameter and returns a response using `self.respond(status_code, response_body)`. the `event` parameter is a dict as passed through from api gateway, so you can use the usual ways of getting query params, headers and post body

you can pass additional parameters from the url path from the route definition using the parameter name within brackets. 

`example(self, event, id, slug)` would use the path `/example/(id)/(slug)` 



#### middleware:
`./lambctl make middleware [name]`

implement `process(self, event)` and return the processed "event"

you can call `self.reject()` to block the request and return a 403 response, or with a custom http status: `self.reject(statusCode, body)`



#### models:
`./lambctl make model [name]`

models are backed by dynamodb. `./lambctl make terraform` will create the terraform files for your tables

`self.table` is the name to use for the table

`self.fillable` is an array of fields which can be updated from the api

`self.indexes` is an array of fields to use as indexes

`Model.get(id)` will return the object of that id from the `Model` table

`Model.find({'index': "query" })` will query the table for models matching a specified index

`Model.save()` will store the object to the db

`Model.delete()` will delete the object from the db



#### public:
the contents of the public folder will be synced to an s3 bucket configured for a single page site, and made available at your domain name. anything you add to this bucket from outside the public folder (ie through the aws console) will be removed on deployment.



#### static:
static is a public s3 bucket with cloudflare set to cache everything. the contents of the static folder will be available at the configured `static_domain_name` (default: `static.[your domain name]`). anything you add to the bucket from ouside the static folder will not be removed



#### lambctl commands:
`./lambctl make command [name]`

implement `run(self, data)` where data is an array of the arguments passed to lambctl 

run the command using `./lambctl [name]`



#### tests:
`./lambctl make test [name]`

You can query the api locally using:

GET: `response = self.getRequest(request)`

POST: `response = self.postRequest(request, postData)`

where `request` is a dict of any event field you wish to override (path, query string parameters, method, headers etc. `{"path":"/ping"}` for example)

and `postData` is a dict to use as the post body



use `self.record(name, result, expected, response)` to track stages of your test

there are helper functions to record output to the terminal with colours where supported:

`self.header(message)`, `self.warn(message)`, `self.success(message="")`, `self.fail(message="")`, `self.skip(message="")`

using `self.fail()` will mark your test as a fail as well as printing output. if the failure does not mean the test is failed, use `self.warn()` instead

your test should `return self.successful`



run all tests using `./lambctl tests`

specify one or more tests to run  `./lambctl tests router`, `./lambctl tests router models`



#### configuration/setup

`./lambctl deploy` will use terraform to deploy/update your site to aws/cloudflare

`-auto-approve` or `-y` will pass the `-auto-approve` flag to terraform



you can use the `lamb.py` file to configure which parts of lamb are enabled [api, db, public, static]

if you modify this file, run `./lambctl make terraform` to regenerate the deployment files for your project

in `lamb.py` you can also specify tests to run before the deployment. use `--ignore-tests` to go ahead with the deployment even if tests fail, or `--skip-tests` to skip the tests entirely



you will need to create a `.env` file and add some terraform variables and aws/cloudflare authentication details

`cp .env.example .env`, add the required values, `source .env`



your zone id is listed on the cloudflare dashboard or you get it with this api call:

```
curl -X GET "https://api.cloudflare.com/client/v4/zones?name=[your domain name]" \
-H "X-Auth-Email: $TF_VAR_cloudflare_email" \
-H "X-Auth-Key: $TF_VAR_cloudflare_apikey" \
-H "Content-Type: application/json"
```



#### manual deployment: 

if you want to follow the deployment process manually: 



(todo:, packages dont work?)

ensure any dependencies are in the `api/package` folder

`pip install -r requirements.txt -t api/package`



create your compiled routes

`./lambctl make routes`



create your terraform definitions

`./lambctl make terraform`



run the tests

`./lambctl tests`



you can then use `terraform [init/plan/apply/destroy]` to control the deployment



#### logs

lamb logs to cloudwatch under `/aws/lambda/lamb_[your domain name]`