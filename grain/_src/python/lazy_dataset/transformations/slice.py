# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Implements slice transformation."""
import dataclasses
import functools
from typing import TypeVar

from grain._src.python.lazy_dataset import lazy_dataset

T = TypeVar("T")


@lazy_dataset.lazy_map_dataset_function("slice")
@dataclasses.dataclass(frozen=False)
class SliceLazyMapDataset(lazy_dataset.LazyMapDataset[T]):
  """Slices a LazyMapDataset similar to the slicing syntax in Python."""

  parent: lazy_dataset.LazyMapDataset[T]
  start: int = 0
  stop: int | None = None
  step: int = 1

  def __post_init__(self):
    sl = slice(self.start, self.stop, self.step)
    self.start, self.stop, self.step = sl.indices(len(self.parent))

  @property
  def sparse(self) -> bool:
    return self.parent.sparse

  @functools.cached_property
  def _length(self) -> int:
    return len(range(self.start, self.stop, self.step))

  def __len__(self) -> int:
    return self._length

  def __getitem__(self, index: int) -> T | None:
    new_index = self.start + (index % self._length) * self.step
    return self.parent[new_index]
