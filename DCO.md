# Developer Certificate of Origin

This project uses the **Developer Certificate of Origin (DCO)** instead of a Contributor License Agreement. The DCO is a lightweight attestation, used by the Linux Kernel and many other open-source projects, that you have the right to submit your contribution under the project's licenses.

## How to sign

Sign off each commit with the `-s` flag:

```bash
git commit -s
```

This appends a `Signed-off-by:` line with your name and email:

```text
Signed-off-by: Jane Doe <jane@example.com>
```

The line must be yours; signing someone else's commit with their permission is acceptable only when they have certified the DCO themselves. To sign an existing commit:

```bash
git commit --amend -s --no-edit
```

To sign your entire branch before pushing:

```bash
git rebase --exec 'git commit --amend --no-edit -s' main
```

CI checks every pull request for this line on every commit.

## The certificate

Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

### Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or

(b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or

(c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.
