# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [3.0.1] - 2021-08-16
### Added
- Github actions config files to test and release

### Changed
- Change mypy config to check kusanagi folder by default
- Change project to run code linting as a separate command
- Change project to run coverage as a separate command

### Fixed
- Fix python versions in pyproject.toml
- Replaced deprecated `Task.all_tasks()`
- Fix AsyncHttpRequest & AsyncResponse private property access

## [3.0.0] - 2021-03-01
### Changed
- Move to poetry for dependency management

## [2.1.1] - 2021-02-27
### Changed
- Remove unused f-strings
- Change copyright year
- Remove version and license import from setup.py

## [2.1.0] - 2020-07-05
### Changed
- Code refactor with typing and pure python3

## [2.0.0] - 2020-03-01
### Fixed
- Fixes Param type resolution when no type is given
- Fixes broken tests
- Handle runtime call exceptions

### Changed
- Adds more tests
- Changes runtime call to save the call into the transport after errors
- Adds `get_timeout()` to ActionSchema
- Adds `get_url_host()` method to HttpRequest
- Fixes `HttpResponse.set_header()` to match new specifications
- Adds flake8 config file
- Changes pylama settings to use github review line length
- Improves `Param.get_value()`
- Changes max line length to 119 to match Github's code review line length
- Update param constructor and add value fallback
- Add overwrite option
- Update language support

## [1.0.1] - 2019-08-17
### Fixed
- Update value of default timeout
- Revise method name

## [1.0.0] - 2019-03-26
- Initial release
