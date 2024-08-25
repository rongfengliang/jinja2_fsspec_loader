from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING,Any

import fsspec
import fsspec.core
import jinja2

if TYPE_CHECKING:
    from collections.abc import Callable


class FsSpecFileSystemLoader(jinja2.BaseLoader):

    ID = "fsspec"

    def __init__(self, fs: fsspec.AbstractFileSystem | str, **kwargs: Any):
        """Constructor.

        Arguments:
            fs: Either a protocol path string or an fsspec filesystem instance.
                Also supports "::dir" prefix to set the root path.
            kwargs: Optional storage options for the filesystem.
        """
        super().__init__()
        if fs:
            if isinstance(fs, str) and "://" in fs:
                self.fs, self.path = fsspec.core.url_to_fs(fs, **kwargs)
            elif isinstance(fs, str):
                self.fs, self.path = fsspec.filesystem(fs, **kwargs), ""
            else:
                self.fs, self.path = fs, ""
        self.storage_options = kwargs
        self.search_path = kwargs.get("search_path", None)

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.storage_options == other.storage_options
            and self.fs == other.fs
            and self.path == other.path
        )

    def __hash__(self):
        return (
            hash(tuple(sorted(self.storage_options.items())))
            + hash(self.fs)
            + hash(self.path)
        )

    def list_templates(self) -> list[str]:
        return [
            f"{path}{self.fs.sep}{f}" if path else f
            for path, _dirs, files in self.fs.walk(self.fs.root_marker)
            for f in files
        ]

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        try:
            if self.search_path:
                template = self.search_path + "/" + template
            with self.fs.open(template) as file:
                src = file.read().decode()
        except FileNotFoundError as e:
            raise jinja2.TemplateNotFound(template) from e
        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True