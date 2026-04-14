# Changelog

All notable changes to this project will be documented in this file.

## Unreleased (2026-04-14)

### Builds

- **deps:** bump actions/github-script from 8 to 9 ([780d017](https://github.com/somaz94/image-tag-updater/commit/780d017d3e0ce0737d52187bba9c6fbc3cc0f03f))
- **deps:** bump softprops/action-gh-release from 2 to 3 ([ef3c9ce](https://github.com/somaz94/image-tag-updater/commit/ef3c9ce52e2cc803002f3f1cdea170c24fbfb0f6))

<br/>

## [v1.5.2](https://github.com/somaz94/image-tag-updater/compare/v1.5.1...v1.5.2) (2026-04-03)

### Code Refactoring

- unify regex constants, modernize types, narrow exceptions, and remove dead code ([2dc8294](https://github.com/somaz94/image-tag-updater/commit/2dc8294a52608c352537b3b6db3fff619ce3f50a))

### Documentation

- remove duplicate rules covered by global CLAUDE.md ([42513b1](https://github.com/somaz94/image-tag-updater/commit/42513b1cb276f48990732e3a969534615df8cc64))

### Chores

- remove duplicate rules from CLAUDE.md (moved to global) ([8f89ee6](https://github.com/somaz94/image-tag-updater/commit/8f89ee63ac42fc52942ac6e60b8fd822c7c02286))
- add git config protection to CLAUDE.md ([0e0daf5](https://github.com/somaz94/image-tag-updater/commit/0e0daf5b5b1470a809a99e184070f1663141ea74))

### Contributors

- somaz

<br/>

## [v1.5.1](https://github.com/somaz94/image-tag-updater/compare/v1.5.0...v1.5.1) (2026-03-25)

### Bug Fixes

- replace sys.exit with ActionError, fix has_staged_changes, add repo validation ([7c8dbb1](https://github.com/somaz94/image-tag-updater/commit/7c8dbb1374c3db64b8ac338a246833d91b4302b8))
- apache license -> mit license ([0848018](https://github.com/somaz94/image-tag-updater/commit/0848018c41c237682d34e7bb63f9f956ae9a32df))
- skip major version tag deletion on first release ([07e1233](https://github.com/somaz94/image-tag-updater/commit/07e1233d24fed707abf149749462f4ba8d620a96))

### Documentation

- add no-push rule to CLAUDE.md ([7faca47](https://github.com/somaz94/image-tag-updater/commit/7faca47aa84b14bf01441170491f4193386fd933))
- update CLAUDE.md with commit guidelines and language ([c001033](https://github.com/somaz94/image-tag-updater/commit/c00103349cbe04ef14e89e9b17c661c9c309dc81))

### Continuous Integration

- skip auto-generated changelog and contributors commits in release notes ([e3c4c83](https://github.com/somaz94/image-tag-updater/commit/e3c4c833f2675dcfb431c35e149b7499ee495a4f))
- revert to body_path RELEASE.md in release workflow ([08a4e87](https://github.com/somaz94/image-tag-updater/commit/08a4e87bdcc9b72276214b2e5320bf183c73079a))
- use generate_release_notes instead of RELEASE.md ([d44fa3e](https://github.com/somaz94/image-tag-updater/commit/d44fa3eeba244a0c831e987045c0077f66379548))
- migrate gitlab-mirror workflow to multi-git-mirror action ([ea3afd2](https://github.com/somaz94/image-tag-updater/commit/ea3afd2cfa384facba1b7517c5fe10991b891dbc))
- use somaz94/contributors-action@v1 for contributors generation ([eaeced3](https://github.com/somaz94/image-tag-updater/commit/eaeced349fc2d877748c0b4d0fc4c7502d16e6e3))
- use major-tag-action for version tag updates ([261c4da](https://github.com/somaz94/image-tag-updater/commit/261c4da03dfbf9a76c389f39d1c4554b709b5828))
- migrate changelog generator to go-changelog-action ([b7b0703](https://github.com/somaz94/image-tag-updater/commit/b7b07030f15094e1f9df97e4340fb01d5741a912))
- add dependabot auto-merge workflow ([ec7ca25](https://github.com/somaz94/image-tag-updater/commit/ec7ca254ce9b9ad7ca799ad807a81689b75ba666))
- unify changelog-generator with flexible tag pattern ([d693e07](https://github.com/somaz94/image-tag-updater/commit/d693e0789d1f1c2ea159a954dbf53e379ed9e268))

### Chores

- change license from MIT to Apache 2.0 ([4a3b98a](https://github.com/somaz94/image-tag-updater/commit/4a3b98a86f535e7f659f832111f6a2238491cba2))

### Contributors

- somaz

<br/>

## [v1.5.0](https://github.com/somaz94/image-tag-updater/compare/v1.4.2...v1.5.0) (2026-03-10)

### Features

- add Makefile, pytest test suite, and dev tooling ([25b07e5](https://github.com/somaz94/image-tag-updater/commit/25b07e519246262000b9d97f52b1cd66ea737d8b))

### Bug Fixes

- correct workflow name in CLAUDE.md and fix template spacing in action.yml ([e12e389](https://github.com/somaz94/image-tag-updater/commit/e12e3894d6b3dcec5f44d2ad2a12d8355c6e335c))

### Code Refactoring

- remove emojis from source and tests, update docs action versions ([54d2609](https://github.com/somaz94/image-tag-updater/commit/54d2609ef1d991c26ad314c762bc0493e8c8656a))
- remove emojis from source code and update docs action versions ([60fe607](https://github.com/somaz94/image-tag-updater/commit/60fe6074b2bbaead09abea6f0477e313b6db20dd))
- align repo conventions with reference repos ([464a1fb](https://github.com/somaz94/image-tag-updater/commit/464a1fb27fb89339726cc01d789df85f04875bfb))
- streamline GitHub Actions workflows and remove linter ([ab3362c](https://github.com/somaz94/image-tag-updater/commit/ab3362c6b46cb9a42b67657b612958030dfd37bd))

### Documentation

- docs/TROUBLESHOOTING.md ([315921a](https://github.com/somaz94/image-tag-updater/commit/315921a32074c62a7cae2211a548a61e5a72cb17))
- update documentation to reflect current project state ([82addc7](https://github.com/somaz94/image-tag-updater/commit/82addc7b5cd9cf32f0b8de84b49f8a6fa2610426))

### Builds

- **deps:** bump docker/setup-buildx-action from 3 to 4 ([806f96f](https://github.com/somaz94/image-tag-updater/commit/806f96f740d27b688255f54bed9a3e54f84bb582))
- **deps:** bump docker/build-push-action from 6 to 7 ([6d805c5](https://github.com/somaz94/image-tag-updater/commit/6d805c53b8a91995aff8dc148931b9eba8d308aa))

### Continuous Integration

- translate workflow comments to English and use conventional commit message ([9efe656](https://github.com/somaz94/image-tag-updater/commit/9efe65608da80dd6bf63e95cab4061c9cb4e51cb))

### Chores

- ci.yml ([587459b](https://github.com/somaz94/image-tag-updater/commit/587459b90504d32ca7c1d60ac75e491d21cdb145))
- remove linter workflow and config files ([b4882dc](https://github.com/somaz94/image-tag-updater/commit/b4882dcfb8eabaab79299420ddb39c66eb683646))

### Contributors

- somaz

<br/>

## [v1.4.2](https://github.com/somaz94/image-tag-updater/compare/v1.4.1...v1.4.2) (2025-12-01)

### Code Refactoring

- main, summary ([0aececd](https://github.com/somaz94/image-tag-updater/commit/0aececd71e023038e99f6765925346df0c8a9664))

### Contributors

- somaz

<br/>

## [v1.4.1](https://github.com/somaz94/image-tag-updater/compare/v1.4.0...v1.4.1) (2025-12-01)

### Code Refactoring

- all code ([25ad06c](https://github.com/somaz94/image-tag-updater/commit/25ad06c17d4b468d8a03a01f74be34ebdc5e67b3))

### Documentation

- tests/README.md ([1c095b9](https://github.com/somaz94/image-tag-updater/commit/1c095b9e5f7c286437e0d07ff6e7f498d4e1d836))
- README.md ([1ca0b89](https://github.com/somaz94/image-tag-updater/commit/1ca0b89d1628115889421874501ee2a562ae3e33))
- README.md ([cb3bd3a](https://github.com/somaz94/image-tag-updater/commit/cb3bd3abf1ca86d8e5e8ae70a299fbe64ccd6701))

### Builds

- **deps:** bump actions/checkout from 5 to 6 ([15ef0ca](https://github.com/somaz94/image-tag-updater/commit/15ef0ca3ecb6389a4971bdbac44b2e8c6e12160f))
- **deps:** bump actions/setup-python from 5 to 6 ([7fe1a88](https://github.com/somaz94/image-tag-updater/commit/7fe1a882f0a1e28a34aa8548681e3fdba99a973d))
- **deps:** bump python in the docker-minor group ([8041241](https://github.com/somaz94/image-tag-updater/commit/804124112d3f114276affd82e3d9c3411ab488ea))

### Chores

- stale-issues, issue-greeting ([c8e2486](https://github.com/somaz94/image-tag-updater/commit/c8e24863a2e473948ad987b68f872d087c86d1f5))
- dockerignore ([3da23d4](https://github.com/somaz94/image-tag-updater/commit/3da23d4e2f92efd434e66906680979fd34409bbe))
- release.yml ([f50a6f7](https://github.com/somaz94/image-tag-updater/commit/f50a6f7cc4a9e25770caba577875b00a80580fe3))
- workflows ([f23a0d4](https://github.com/somaz94/image-tag-updater/commit/f23a0d486e3d6fae03c86794feb7a5c8d3d88248))

### Contributors

- somaz

<br/>

## [v1.4.0](https://github.com/somaz94/image-tag-updater/compare/v1.3.0...v1.4.0) (2025-10-30)

### Code Refactoring

- all ([4869f75](https://github.com/somaz94/image-tag-updater/commit/4869f75dc57a25157a42bffbc91ca37920289077))

### Chores

- ci.yml, use-action.yml & docs: README.md ([6f2597f](https://github.com/somaz94/image-tag-updater/commit/6f2597f55bfaa4d86515869ce52a4c316341cacb))
- action.yml, main.py, ci.yml ([5e8b6b7](https://github.com/somaz94/image-tag-updater/commit/5e8b6b7a45a135f627162d018c4200257e4b73a1))
- ci.yml ([0ac2080](https://github.com/somaz94/image-tag-updater/commit/0ac208064ae43d9ba67e329d99510d70aeb9569b))
- ci.yml ([add64b1](https://github.com/somaz94/image-tag-updater/commit/add64b12fe005c1390fadc84be3eaa6f23771211))
- qa1.values.yaml ([cce8ba1](https://github.com/somaz94/image-tag-updater/commit/cce8ba17aea0f829410b51c4aefd51e034453171))
- use-action.yml ([74065a1](https://github.com/somaz94/image-tag-updater/commit/74065a1654edd686bd7c6887d0cf2496bca2b1e0))
- use-action.yml ([288c344](https://github.com/somaz94/image-tag-updater/commit/288c344adb54d7c9b8d90a0d219386815b02a5a9))

### Refatcor

- fr ([8513c00](https://github.com/somaz94/image-tag-updater/commit/8513c0005f5b1b07dd362e151c8f0ad74af876d7))

### Contributors

- somaz

<br/>

## [v1.3.0](https://github.com/somaz94/image-tag-updater/compare/v1.2.2...v1.3.0) (2025-10-30)

### Code Refactoring

- all ([95a274f](https://github.com/somaz94/image-tag-updater/commit/95a274f556761091f6cf57c3fd258713d7362cc6))
- bash -> python ([7825b26](https://github.com/somaz94/image-tag-updater/commit/7825b26ec48264750f6656ad2f829a2aa6b09777))

### Documentation

- README.md, chore: github workflow ([44734e2](https://github.com/somaz94/image-tag-updater/commit/44734e276a7140f4a3ed2e7644ea3c0c8f97d1a9))

### Builds

- **deps:** bump actions/checkout from 4 to 5 ([785693e](https://github.com/somaz94/image-tag-updater/commit/785693eecee19db4cc1a6e6a911bd9e6e915b02d))
- **deps:** bump super-linter/super-linter from 7 to 8 ([d55dbd6](https://github.com/somaz94/image-tag-updater/commit/d55dbd6dc0f8cf4f259f4c29ddf4cc1b2d98bb9b))
- **deps:** bump alpine from 3.21 to 3.22 in the docker-minor group ([e914037](https://github.com/somaz94/image-tag-updater/commit/e91403759dbc94505934ef05a802d5b5ac37680b))

### Chores

- logger.py ([b5b330f](https://github.com/somaz94/image-tag-updater/commit/b5b330fae6b99151145cf34900ef3d24a9de6ba8))
- delete emoji ([0b0a488](https://github.com/somaz94/image-tag-updater/commit/0b0a48866087ab34a6c882876b27bf9e8540cd4b))

### Contributors

- somaz

<br/>

## [v1.2.2](https://github.com/somaz94/image-tag-updater/compare/v1.2.1...v1.2.2) (2025-04-15)

### Bug Fixes

- entrypoint.sh ([0b53dd4](https://github.com/somaz94/image-tag-updater/commit/0b53dd4b8eeab84be80b52e74b8a76dc7e9c9b3e))

### Contributors

- somaz

<br/>

## [v1.2.1](https://github.com/somaz94/image-tag-updater/compare/v1.2.0...v1.2.1) (2025-04-11)

### Bug Fixes

- use-action.yml ([f2da484](https://github.com/somaz94/image-tag-updater/commit/f2da48452716369435b427e21373a1f6f0bee115))
- ci.yml ([088ad72](https://github.com/somaz94/image-tag-updater/commit/088ad72595a40428f43565e03b2fbfa57655699f))
- ci.yml ([e9c2664](https://github.com/somaz94/image-tag-updater/commit/e9c26641fdbab83058de513dfd18d12473a0eb90))
- changelog-generator.yml ([4e0dc70](https://github.com/somaz94/image-tag-updater/commit/4e0dc70f04722472f0fac112caa68f62a459352e))
- use-action-v2.yml ([31a0c9c](https://github.com/somaz94/image-tag-updater/commit/31a0c9cc8a882aa2b92708149e48283dc93a4b00))

### Documentation

- README.md, entrypoint.sh ([797be8f](https://github.com/somaz94/image-tag-updater/commit/797be8fcfc32b9f6f6ddc678acf22f2f223c56e1))

### Add

- gitlab-mirror.yml ([fd3ed8f](https://github.com/somaz94/image-tag-updater/commit/fd3ed8f7343b992b3cc9a2aaae09af717046f9ca))
- gitlab-mirror.yml ([c4f258d](https://github.com/somaz94/image-tag-updater/commit/c4f258d408a0db104185e349cd0c02be612d7531))

### Contributors

- somaz

<br/>

## [v1.2.0](https://github.com/somaz94/image-tag-updater/compare/v1.1.0...v1.2.0) (2025-02-20)

### Bug Fixes

- entrypoint.sh ([d31e74b](https://github.com/somaz94/image-tag-updater/commit/d31e74be4a9a8c953b01c7ecf75f39c08121d436))
- entrypoint.sh, ci.yml ([f510df3](https://github.com/somaz94/image-tag-updater/commit/f510df313e2f695ef008d7307e745abc97893bb5))
- entrypoint.sh ([eb91119](https://github.com/somaz94/image-tag-updater/commit/eb91119ba60b7d6856745848433dad5a8d7d4c2b))
- backup ([a4d83e1](https://github.com/somaz94/image-tag-updater/commit/a4d83e1d0f5f3aaa6930fdb2940b5a938449ca68))
- ci.yml ([19de861](https://github.com/somaz94/image-tag-updater/commit/19de86142b8f6a18c8441e50d3e6861ae51b517a))
- entrypoint.sh, ci.yml ([994844a](https://github.com/somaz94/image-tag-updater/commit/994844a004a350c2533af282857294e3ed0d688f))
- ci.yml, entrypoint.sh ([150161e](https://github.com/somaz94/image-tag-updater/commit/150161eb4952e7d1a2e0256d4b337cad86f486ba))
- ci.yml ([f79db1f](https://github.com/somaz94/image-tag-updater/commit/f79db1fca1ab64af7bb09671430722d778e86c04))
- ci.yml, entrypoint.sh ([4a5c4a6](https://github.com/somaz94/image-tag-updater/commit/4a5c4a6fee64289d32f1c65cc8648740979af7dd))
- ci.yml, action.yml, entrypoint.sh ([939ee86](https://github.com/somaz94/image-tag-updater/commit/939ee866811f40bfd51b99f0f4deb60383f78608))
- backup ([50d2d51](https://github.com/somaz94/image-tag-updater/commit/50d2d515f951255a3336f2930b1a6acdfe4643c0))
- entrypoint.sh ([df04e9f](https://github.com/somaz94/image-tag-updater/commit/df04e9f1109489408f9f018505bb848751e512f5))
- bakcup/entrypoint.sh ([9632980](https://github.com/somaz94/image-tag-updater/commit/9632980291e21e39e89226bc4cefc2738636b19a))
- ci.yml ([dee7cec](https://github.com/somaz94/image-tag-updater/commit/dee7cecc6349d9c632e77978012f651c8c9c7ee3))
- changelog-generator.yml ([733bf83](https://github.com/somaz94/image-tag-updater/commit/733bf83e6d44dab4c432aed88d9ab402eacd8c2a))

### Documentation

- README.md ([c61aee6](https://github.com/somaz94/image-tag-updater/commit/c61aee6a14a64683969a5595cb10943f09f7b00f))

### Contributors

- somaz

<br/>

## [v1.1.0](https://github.com/somaz94/image-tag-updater/compare/v1.0.1...v1.1.0) (2025-02-13)

### Bug Fixes

- all file ([ca40256](https://github.com/somaz94/image-tag-updater/commit/ca40256238cf49286bdb7bad4d25e58412db2784))
- entrypoint.sh ([4a22bc5](https://github.com/somaz94/image-tag-updater/commit/4a22bc561983f253f417476d29096d0ba3703e42))
- entrypoint.sh ([3f016e3](https://github.com/somaz94/image-tag-updater/commit/3f016e33582a95f33bcd7ad66a97ee9fc6efcf15))
- entrypoint.sh ([acf4970](https://github.com/somaz94/image-tag-updater/commit/acf4970a14d710a06232bf2c9312730f85d8d50f))
- entrtypoint.sh ([cb3de43](https://github.com/somaz94/image-tag-updater/commit/cb3de4339ea8f0128193519aed6ad9156da32a09))
- entrtypoint.sh ([917ca47](https://github.com/somaz94/image-tag-updater/commit/917ca4716ae759271d0968b35ae3a6cde92dd3cb))
- entrypoint.sh ([c01ae6f](https://github.com/somaz94/image-tag-updater/commit/c01ae6f1c14a530708f200213fc71acaaeb44c57))
- entrypoint.sh ([b5b27f8](https://github.com/somaz94/image-tag-updater/commit/b5b27f8fe0ae0773c885f5b82bc91f64f5bdb4fe))
- entrypoint.sh ([29c6693](https://github.com/somaz94/image-tag-updater/commit/29c669371fa36b2eb464f7e90ecc281e7ea61dfe))
- entrypoint.sh ([0540c11](https://github.com/somaz94/image-tag-updater/commit/0540c11bf626fa4979682e3accc6c3faf78f0a46))
- all file ([bf6be38](https://github.com/somaz94/image-tag-updater/commit/bf6be38b8f6c26da7d97757ee1d45b04fd1feba1))
- ci.yml ([ab9149c](https://github.com/somaz94/image-tag-updater/commit/ab9149c82471ed57ed3cdef96cc45d08bdf8edab))
- ci.yml , use-action.yml, action.yml, entrypoint.sh ([88c3f5e](https://github.com/somaz94/image-tag-updater/commit/88c3f5e909318dd4b050905c665584e2e491b627))
- entrypoint.sh ([327f390](https://github.com/somaz94/image-tag-updater/commit/327f3905696d61e3de0b65dcd7dc63a78da5eb18))
- action.yml ([d9c9a2a](https://github.com/somaz94/image-tag-updater/commit/d9c9a2a8db26771bf10f1d176ab4db275d39f83f))

### Documentation

- README.md & action.yml ([8a4d59b](https://github.com/somaz94/image-tag-updater/commit/8a4d59b36845af0a7295572636ed1576af2e52d4))

### Contributors

- somaz

<br/>

## [v1.0.1](https://github.com/somaz94/image-tag-updater/compare/v1.0.0...v1.0.1) (2025-02-07)

### Bug Fixes

- ci.yml & use-action.yml ([e8829a4](https://github.com/somaz94/image-tag-updater/commit/e8829a4925e06ee49ada8c279df2e5d87fc39e27))
- use-action.yml ([bfc4c2b](https://github.com/somaz94/image-tag-updater/commit/bfc4c2bdab43ed0ed662106919be927689ff18b6))
- Dockerfile ([e773df2](https://github.com/somaz94/image-tag-updater/commit/e773df2343797dd5e7b28ad0bbc23b346a3a23be))
- chagnelog-generator.yml ([fb5c36c](https://github.com/somaz94/image-tag-updater/commit/fb5c36cfe2f5b26fb8e32325f909705e715ba2a2))
- ci.yml ([688ce63](https://github.com/somaz94/image-tag-updater/commit/688ce635ebf97db05e8f038a93746de99517739e))
- entrypoint.sh ([f0fc841](https://github.com/somaz94/image-tag-updater/commit/f0fc841243f0319b9715f99819e15ae6259600cb))

### Documentation

- README.md ([6426a10](https://github.com/somaz94/image-tag-updater/commit/6426a10dcdc509a6568936246e920da90fe3d5cc))

### Contributors

- somaz

<br/>

## [v1.0.0](https://github.com/somaz94/image-tag-updater/releases/tag/v1.0.0) (2025-02-05)

### Bug Fixes

- use-action-v2.yml ([d3cc5f6](https://github.com/somaz94/image-tag-updater/commit/d3cc5f625e346241536d30f62500b32868e5aa17))
- .github/workflows/use-action.yml ([f23ab61](https://github.com/somaz94/image-tag-updater/commit/f23ab610ee0591eb383c6bf83d47f79c56e5a69e))
- .github/workflows/use-action.yml ([f9143db](https://github.com/somaz94/image-tag-updater/commit/f9143db5c807f1741014932db8516a6dcd961e92))
- entrypoint.sh ([f73187c](https://github.com/somaz94/image-tag-updater/commit/f73187cafc52e01529d18601834c7f3b4b4ba2b3))
- entrypoint.sh ([6b08074](https://github.com/somaz94/image-tag-updater/commit/6b080749fc392b612adfad0a722dc8339aa7c169))

### Code Refactoring

- workflow, lint, Dockerfile, entrypoint.sh ([1d8ea1c](https://github.com/somaz94/image-tag-updater/commit/1d8ea1cced52dad0c5f0a37b156b2e1a68a08416))
- workflow, lint, Dockerfile ([c21cf24](https://github.com/somaz94/image-tag-updater/commit/c21cf240ae38756864425e17064621898a63a868))
- workflow, lint, Dockerfile ([50cfcb1](https://github.com/somaz94/image-tag-updater/commit/50cfcb1253839bd5d00942e0ad62d1b80cad8965))

### Documentation

- CODEOWNERS ([7e54c7a](https://github.com/somaz94/image-tag-updater/commit/7e54c7a42a78f110b5aa2a09bf0649543d42d2ce))
- README.md ([59e120a](https://github.com/somaz94/image-tag-updater/commit/59e120ab859edb8ae1b8ac34dd3b00cc93395891))
- README.md ([2fc1b9f](https://github.com/somaz94/image-tag-updater/commit/2fc1b9f33838066d45dc2705621ebe8e6d030961))
- README.md ([fe1575e](https://github.com/somaz94/image-tag-updater/commit/fe1575eb77d6e72386d81748b7ab96b6c04b251c))
- README.md ([0a0e9b5](https://github.com/somaz94/image-tag-updater/commit/0a0e9b53fec20fc378eda656f1376e1f4973c034))
- README.md ([3d188bc](https://github.com/somaz94/image-tag-updater/commit/3d188bcdf6efb492f115612bc90abf9e71f872af))

### Builds

- **deps:** bump janheinrichmerker/action-github-changelog-generator ([1dc6c82](https://github.com/somaz94/image-tag-updater/commit/1dc6c8244ba79416a2e73931f47cf52a8f6dff9c))
- **deps:** bump alpine from 3.20 to 3.21 in the docker-minor group ([9f995be](https://github.com/somaz94/image-tag-updater/commit/9f995bedf67527ceb3ad27bc6e9242c00cf042b3))

### Chores

- add dependabot.yml.example ([881afd5](https://github.com/somaz94/image-tag-updater/commit/881afd59347d567d16974332538b4c31283be251))
- fix dependabot.yml ([e0b913c](https://github.com/somaz94/image-tag-updater/commit/e0b913c14ce9a9f7bb30fa00e8430bd096992dd3))
- fix changelog-generator.yml ([221c650](https://github.com/somaz94/image-tag-updater/commit/221c65065e244ef34d76783315ccae6bca5a72c7))
- fix changelog workflow ([d807b82](https://github.com/somaz94/image-tag-updater/commit/d807b82dd82dd3a0b705a5d8dede0af4f85deb37))
- add changelog workflow ([6720b2f](https://github.com/somaz94/image-tag-updater/commit/6720b2fc950e0234fc2e53e55e2927355f6098eb))

### Contributors

- somaz

<br/>

