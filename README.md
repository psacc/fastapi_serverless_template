# README

## Quickstart

Start up immediately with:

```
$./cli setup # if not running in the provided dev container
$./cli lint # performs static analysis and vulnerability scanning
$./cli test # runs all the tests with coverage reporting
$./cli serve # run a local instance
$./cli test_e2e # e2e tests (by default using the local instance endpoint)
$./cli deploy # deploy on aws as lambda + apigwv2
```

## Development notes and design

### Scope

This is a coding exercise, nonetheless I tried my best at making it production ready in the time allowed. Where limitations apply those will be highlighted and explained in the following. Reference documentation links are available in the [#appendix](./#appendix "mention").

### Requirements

This component is an URL shortener service, usually these services provide functionalities such as:

* **Shortening URLs**: Converting long URLs into short, manageable links.
* **Redirecting Users**: Redirecting users from the short URL to the original URL.
* **Tracking and Analytics**: Providing data on the number of clicks, geographical location of the clicks, and other metrics.
* **Custom Aliases**: Allowing users to create custom short URLs.
* **Managing Links**: Offering options to edit or delete shortened URLs.
* **Security**: Preventing spam or malicious links by scanning or filtering URLs.

We will be solely focusing on the basic operations of:

* **encoding an URL to its shortened version**
* **decoding the shortened version of a URL to the original one**

Such functionalities are part of a API back-end component and does not take into account the front-end that provides the actual mean to route the client when navigates to a shortened URL and the UI to shorten the original ones (in short UI and web routing).

### Design decisions

Before starting the actual coding, I've made some design decisions, usually those are discussed with a team and recorded in a log for reference, here we skipped having a formal record and just write the most relevant in this section:

1. **Have a reproducible dev environment**, that can avoid being tied to local resources: Dev Containers support this use case well and are supported by Github Codespaces, allowing to use a Visual Studio Code instance remotely.
2. **Define the APIs contract first**, it is not the easiest and fastest way, but in the context of this exercise serves the purpose of using a common approach in enterprise environments, allowing for example a different team to develop a frontend in parallel without waiting for the real backend to be available. We will use OpenAPI as the specification format to describe the APIs contract.
3. **Url shortening algorithm**, there are a ton of options, but in order to show some business logic in this exercise we opt to use for a hashing function (SHA256) to decouple input from output securely, truncating it to the first 10 bytes in order to make it suitable for short urls and then encoding with BASE62 for readability of the resulting URL. Collisions should be taken into account using linear progression, and since we don't support deletions, the iteration added to the hash creation to disambiguate can be discarded, storing only the result. We want to reuse well know implementations for SHA256 and BASE62.
4. **Datastore is in memory**, nonetheless we want to be decoupled from the implementation and assume it will be possibly asynchronous.
5. **Use AWS as target cloud provider**, specifically using lambda and APIGW, this is mostly an assumption, we don't want the actual implementation to be directly tied to the specific cloud provider, while allowing to have a deployment target that is not local.&#x20;

### Implementation

This sections describes the development story of the assignment to allow a better grasp of what happens during this phase and what should actually happen in a real development scenario.

#### Versioning

Working solo changes a lot, I've tried to show off what would happen in a real (team based) development scenario. I've used a private github repo and then pushed the result to the codesubmit one.

GitHub repo: [https://github.com/psacc/finn-codesubmit/](https://github.com/psacc/finn-codesubmit/) (I can make it public if you agree or allow access to specific users, but it is not required to complete the evaluation).

This allowed to work with pull requests, simulating reviews and let me have a linear history in main/master. I've worked on feature branches, often switching feature as I were understanding how to best make it fit, but with the general guideline of following a merge order that will go as:

1. setup dev tooling
2. define the contract
3. implement the code and tests locally
4. add support for deployment and e2e tests
5. documentation
6. eventual bugfixes

#### Development environment

As mentioned, I've worked with Visual Studio Code mostly in a Codespace (additional reason to use GitHub). This is not in any way required. An IDE that support Dev Containers should be preferred, since that is the versioned descriptor that tracks the development environment. It easy enough to work without it provided that you have installed the correct versions of `python` and `node` stated in `devcontainer.json`.

To kick start development I've would have used a Cookiecutter template (see [#appendix](./#appendix "mention")), but none suited the exact scope of this exercise, so I went on with `poetry` to have a base with some of the best pracrices for development.

I've also added a very simple `cli` shell wrapper, mostly to be quicker, probably the most part of it can be substituted with additional `poetry` configuration.

Using `./cli setup` allows to easly prepare the container with all that is required in order to contribute code. It installs dependencies and configure local pre-commit hooks.

Instead `./cli autoupdate` can serve when there are outdated dependencies, this is usually rare, especially if there is a CI with checks for stale dependencies in place, more on this later.

#### &#x20;Continuous integration / deployment (CI/CD)

In this exercise, I've avoided setting up CI/CD pipelines, nonetheless, the code to implement them is there and can be summarized as:

`./cli setup && ./cli lint && ./cli test`

Also linting is performed on commits using `pre-commit` and the `cli` uses it to ensure the same checks are performed. That is ideal for a CI environment and leaves adding a GitHub action to ensure those checks are performed before a pull request is merged as a trivial task.

Going into more detail about the linting checks without explaining the whole `.pre-commit-config.yaml` (that is better served by reading the official docs mentioned in [#appendix](./#appendix "mention")) i want to mention:

* ruff [https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff), that is a very fast python linter, drop-in parity with [Flake8](https://docs.astral.sh/ruff/faq/#how-does-ruff-compare-to-flake8), isort, and Black
* skijold [https://github.com/twu/skjold](https://github.com/twu/skjold), that is the security scanner I've chosen, surely not the best, it serves the purpose to show that vulnerability scanning is important (more on security later)

#### Service implementation and testing

As already mentioned, for the implementation I used a contract fist approach. That is not very well supported in terms of tooling as is far less widely used especially for small projects. Authoring the specification is the easy part, the difficult is to generate the conform implementation.

To implement the APIs, I've chosen to use FastAPI, as it a full featured lightweight framework to do just that. One of the reasons why it is fast is that promotes the usage of asynchronous calls, to work around the limitation that python has with multi-threading (I'm coming from a Java background in saying this).

Unfortunately, FastAPI does not promote a contact first development model, rather the opposite. Anyway I've looked at tools that allows for this approach with it:

* (discarded) [https://openapi-generator.tech/docs/generators/python-fastapi/](https://openapi-generator.tech/docs/generators/python-fastapi/) this generator has official OpenAPI support, but has the approach of generate once and the code, it is full featured, but much opinionated in terms of the resulting code structure, it may fit well for bigger projects investing some time, but in the context of this exercise it would limit too much and over-complicate the implementation of the business logic.
* (chosen) [https://github.com/ioxiocom/openapi-to-fastapi](https://github.com/ioxiocom/openapi-to-fastapi) this tool is very limited (supports only posts verbs currently), but generates the models from the specification and allows easy mapping of the APIs implementation without using a generative approach, for the scope of the exercise it is good enough, but only because the design of the contract is within the scope of activities.

With FastAPI configured to use the API contract we benefit from having a simple way to run the service also locally, without additional infrastructure, with `./cli serve`.

The rest of the production code, aside from boilerplate, is divided into:

* The routes defined to support encode and decode operations, those handle formal validation and HTTP translation;
* The URL shortener business logic used by the routes, this implements the shortening logic described in the design, using [https://github.com/suminb/base62](https://github.com/suminb/base62?tab=readme-ov-file) and the SHA256 implementation provided in the python standard library;
* The datastore abstraction, that provides an in memory implementation with a dict and it is used by the URL shortener to persist and lookup the data it generates.

Testing is done with a test driven approach where possible, to ensure mostly corner cases are handled, but I did not aim to have a 100% coverage (that is measured via `./cli test`), rather to cover the functionality and thus testing from the APIs perspective wherever possible. And in this regard FastAPI allows for testing that are identical to using an HTTP client very easily.

Deployment and e2e tests

To create the AWS infrastructure and deploy the APIs, I've evaluated:

* (discarded) AWS Chalice, because it is a micro-framework, completely in python, that can create the required infrastructure by using annotation to the code while still allowing to export to Cloudformation or Terraform and use it only for packaging. It proved too difficult to adapt it to work with FastAPI, while leaving FastAPI for it would have complicated testing and running locally. It is a valuable option if working on an AWS specific solution and in the context of this exercise I wanted a backend that can work on AWS, but can be as easily deployed elsewhere.
* (chosen) Serverless Framework, is opinionated but very flexible. It suits well the case to start fast like for this exercise, but I would look at a different option (either investing in Terraform or CDK) for bigger projects, because it tries to create ties with its own infrastructure (the so called Severless Dashboard) that is used by default (as of version 4 of the framework) to operate on AWS.

With Serverless it easy to create different environment, for the scope of this exercise I've create just the `dev` one but more can be easily added in `serverless.yml`. The command `./cli deploy` simply assumes the `dev` environment.

I've provided also a `./cli test_e2e` that execute a subset of tests against a provided endpoint either a local instance started with `./cli serve` or a remote one created with `./cli deploy`.

The test executed are limited to the ones that use the `httpx` python HTTP client, those are end-to-end but are used also without a live server thanks to the FastAPI client.

I've also added Schemathesis (see [#appendix](./#appendix "mention")) to ensure better conformity to the OpenAPI specification with tests that generate random data by inspecting the declared operations and types.

#### Performance, monitoring and observability

For this part I've added a basic structured JSON logging.

There was no space to go trough an opinionated implementation of the observability part. Most of it is filled by using Serverless (metrics, log gathering, tracing), but as mentioned earlier, one should rather look to a solution that fits with the overall enterprise, that may be based on AWS Cloudwatch or Datadog.

Also I left out any performance testing. That should be required for every at least major production deployment and serves to validate also sizing of the components (memory, space, CPU). I here have left to the defaults of the cloud provider.

And finally part of the infrastructure should be running canary tests continuously on the production instance to ensure that if there are anomalies those are caught up early, before the users can notice.

#### Security considerations

Addressing all security concerns is very time consuming. What I've done here is twofold:

* Concentrate on the possible threats from a functional perspective: those are very limited and as stated in [#requirements](./#requirements "mention") I've left out of scope scanning the security of the URLs provided to the APIs, nonetheless there are services that could be used for this purpose of warning or avoiding redirecting users to addresses that are known to be malicious.
* Ensure dependencies are scanned for vulnerabilities, as supply-chain attacks grow in popularity this is more relevant. Still in an enterprise environment all software should be provisioned from trusted sources, resulting built artifacts should provide immutable dependencies descriptors (SBOMs) and support build reproducibility. This was out of scope for this exercise sadly.
* Authentication / Authorization is not implemented, nor should be directly in the code that handles the logic, it can be added declaratively (via Serverless for example).
* Environment configuration and secrets handling is not shown, as Serverless supports it would not have added much in terms of the logic to implement.

#### Documentation

To author the documentation I've used [https://gitbook.com](https://gitbook.com) as it sits in a good middle ground between code friendly and writing friendly, as I value having good written documentation while also the code should be clear and easy to read.

## Appendix

Here is a list of the relevant documentation links to go deeper and for reference:

Dev Containers: [https://containers.dev/](https://containers.dev/templates)

Cookiecutter: [https://cookiecutter.readthedocs.io/](https://cookiecutter.readthedocs.io/)

Poetry: [https://python-poetry.org](https://python-poetry.org)

Pre-Commit: [https://pre-commit.com](https://pre-commit.com)

Serverless framework

* [https://www.serverless.com/framework/docs](https://www.serverless.com/framework/docs)
* [https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml)
* [https://www.serverless.com/plugins/serverless-openapi-plugin](https://www.serverless.com/plugins/serverless-openapi-plugin)

AWS Chalice: [https://aws.github.io/chalice/](https://aws.github.io/chalice/index.html)

FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

OpenAPI

* [https://learn.openapis.org/](https://learn.openapis.org/)
* [https://tools.openapis.org/categories/code-generators.html](https://tools.openapis.org/categories/code-generators.html)
* [https://github.com/ioxiocom/openapi-to-fastapi](https://github.com/ioxiocom/openapi-to-fastapi)
* [https://openapi-generator.tech/docs/generators/python-fastapi/](https://openapi-generator.tech/docs/generators/python-fastapi/) requires node, much more opinionated

Schemathesis

* [https://schemathesis.readthedocs.io/en/stable/](https://schemathesis.readthedocs.io/en/stable/)
* [https://github.com/schemathesis/schemathesis](https://github.com/schemathesis/schemathesis)

Inspiration:

* [https://dev.to/nimishverma/a-guide-to-start-a-fastapi-poetry-serverless-project-142d](https://dev.to/nimishverma/a-guide-to-start-a-fastapi-poetry-serverless-project-142d)
* [https://github.com/NimishVerma/ServerlessFastapiPoetry](https://github.com/NimishVerma/ServerlessFastapiPoetry)
