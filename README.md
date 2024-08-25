# jinja2 fsspec loader 


## Usage

> need install ossfs

```code
from fsspec_loader import FsSpecFileSystemLoader
loader = FsSpecFileSystemLoader("oss", endpoint='xxx',key="xxxxx",secret="xxxxx",search_path=template_dir)
env = j2.Environment(loader=loader)
```