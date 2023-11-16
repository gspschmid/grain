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
"""Tests for mixing transformation."""

import sys

from absl.testing import absltest
from grain._src.python.lazy_dataset import lazy_dataset
from grain._src.python.lazy_dataset.transformations import mix
from grain._src.python.lazy_dataset.transformations import repeat  # pylint: disable=unused-import
import numpy as np


class MixedLazyMapDatasetTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.even_ds = lazy_dataset.RangeLazyMapDataset(0, 10, 2)
    self.odd_ds = lazy_dataset.RangeLazyMapDataset(1, 10, 2)

  def test_len(self):
    # Mix dataset has length to see any element at most once.
    ds1 = lazy_dataset.RangeLazyMapDataset(10)
    ds2 = lazy_dataset.RangeLazyMapDataset(20)
    ds3 = lazy_dataset.RangeLazyMapDataset(5)
    # Equal proportions.
    ds = mix.MixedLazyMapDataset([ds1, ds2, ds3])
    self.assertLen(ds, 15)
    # Heigher weight for second dataset.
    ds = mix.MixedLazyMapDataset([ds1, ds2, ds3], proportions=[1, 2, 1])
    self.assertLen(ds, 5 + 10 + 5)

  def test_mixing_equal_probability_with_integer_proportions(self):
    mixed_lzds = mix.MixedLazyMapDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[2, 2]
    )
    actual_values = [mixed_lzds[i] for i in range(10)]
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_equal_probability_with_float_proportions(self):
    mixed_lzds = mix.MixedLazyMapDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[0.5, 0.5]
    )
    actual_values = [mixed_lzds[i] for i in range(10)]
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_equal_probability_with_no_proportions_given(self):
    mixed_lzds = mix.MixedLazyMapDataset(parents=[self.even_ds, self.odd_ds])
    # If no proportions specified, parents are mixed in equal proportions.
    actual_values = [mixed_lzds[i] for i in range(10)]
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_with_float_proportions(self):
    mixed_lzds = mix.MixedLazyMapDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[0.75, 0.25]
    )
    self.assertLen(mixed_lzds, 6)

    actual_vals = list(mixed_lzds)
    expected_frist_epoch = [0, 2, 4, 1, 6, 8]
    self.assertEqual(actual_vals, expected_frist_epoch)

    actual_vals = list(mixed_lzds.repeat(2))
    expected_two_epochs = [
        0,
        2,
        4,
        1,
        6,
        8,
        0,
        3,
        2,
        4,
        6,
        5,
    ]
    self.assertEqual(actual_vals, expected_two_epochs)

  def test_mixing_with_integer_proportions(self):
    mixed_lzds = mix.MixedLazyMapDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[1, 2]
    )
    self.assertLen(list(mixed_lzds), 7)

    actual_values = list(mixed_lzds)
    expected_first_epoch = [0, 1, 3, 2, 5, 7, 4]
    self.assertEqual(expected_first_epoch, actual_values)

    actual_values = list(mixed_lzds.repeat(2))
    expected_two_epochs = [0, 1, 3, 2, 5, 7, 4, 9, 1, 6, 3, 5, 8, 7]
    self.assertEqual(expected_two_epochs, actual_values)

  def test_mixing_zero_one_probability_fails_with_error(self):
    with self.assertRaises(ValueError):
      _ = mix.MixedLazyMapDataset(
          parents=[self.even_ds, self.odd_ds], proportions=[0, 1]
      )

  def test_mix_infinite_datasets(self):
    zeros = lazy_dataset.RangeLazyMapDataset(0, 1).repeat()
    ones = lazy_dataset.RangeLazyMapDataset(1, 2).repeat()
    self.assertLen(zeros, sys.maxsize)
    self.assertLen(ones, sys.maxsize)
    ld = mix.MixedLazyMapDataset([zeros, ones], proportions=[4, 1])
    self.assertLen(ld, sys.maxsize)
    # Mix again.
    ld = mix.MixedLazyMapDataset([ld, ones], proportions=[1, 1])
    num_samples = 1000
    value_counts = np.bincount([ld[i] for i in range(num_samples)]).tolist()
    self.assertEqual(value_counts, [400, 600])


class MixedLazyIterDatasetTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.even_map_ds = lazy_dataset.RangeLazyMapDataset(0, 10, 2)
    self.odd_map_ds = lazy_dataset.RangeLazyMapDataset(1, 10, 2)
    self.even_ds = self.even_map_ds.to_iter_dataset()
    self.odd_ds = self.odd_map_ds.to_iter_dataset()

  def test_len(self):
    # Mixed dataset sees any element at most once.
    ds1 = lazy_dataset.RangeLazyMapDataset(10).to_iter_dataset()
    ds2 = lazy_dataset.RangeLazyMapDataset(20).to_iter_dataset()
    ds3 = lazy_dataset.RangeLazyMapDataset(5).to_iter_dataset()
    # Equal proportions.
    ds = mix.MixedLazyIterDataset([ds1, ds2, ds3])
    # While ds3 is empty after sampling 15 elements, a StopIteration is raised
    # when an example is sampled from ds3 the next time; an example is sampled
    # from ds1 and ds2 before then; hence the size of the mixed dataset is 17
    # instead of 15.
    self.assertLen(list(ds), 17)
    # Heigher weight for second dataset.
    ds = mix.MixedLazyIterDataset([ds1, ds2, ds3], proportions=[1, 2, 1])
    # ds1 is sampled from once and ds2 is sampled from twice before
    # StopIteration is raised by ds3
    self.assertLen(list(ds), 6 + 12 + 5)

  def test_mixing_equal_probability_with_integer_proportions(self):
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[2, 2]
    )
    actual_values = list(mixed_lzds)
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_equal_probability_with_float_proportions(self):
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[0.5, 0.5]
    )
    actual_values = list(mixed_lzds)
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_equal_probability_with_no_proportions_given(self):
    mixed_lzds = mix.MixedLazyIterDataset(parents=[self.even_ds, self.odd_ds])
    # If no proportions specified, parents are mixed in equal proportions.
    actual_values = list(mixed_lzds)
    expected_values = [val for val in range(10)]
    self.assertEqual(expected_values, actual_values)

  def test_mixing_with_float_proportions(self):
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[0.75, 0.25]
    )
    actual_vals = list(mixed_lzds)
    expected_frist_epoch = [0, 2, 4, 1, 6, 8]
    self.assertEqual(actual_vals, expected_frist_epoch)

    # Mix with repeats.
    ds1 = self.even_map_ds.repeat(2).to_iter_dataset()
    ds2 = self.odd_map_ds.repeat(2).to_iter_dataset()
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[ds1, ds2], proportions=[0.75, 0.25]
    )
    actual_vals = list(mixed_lzds)
    expected_two_epochs = [0, 2, 4, 1, 6, 8, 0, 3, 2, 4, 6, 5, 8]
    self.assertEqual(actual_vals, expected_two_epochs)

  def test_mixing_with_integer_proportions(self):
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[1, 2]
    )
    self.assertLen(list(mixed_lzds), 8)

    actual_values = list(mixed_lzds)
    expected_first_epoch = [0, 1, 3, 2, 5, 7, 4, 9]
    self.assertEqual(expected_first_epoch, actual_values)

    # Mix with repeats.
    ds1 = self.even_map_ds.repeat(2).to_iter_dataset()
    ds2 = self.odd_map_ds.repeat(2).to_iter_dataset()
    mixed_lzds = mix.MixedLazyIterDataset(
        parents=[ds1, ds2], proportions=[1, 2]
    )
    actual_values = list(mixed_lzds)
    expected_two_epochs = [0, 1, 3, 2, 5, 7, 4, 9, 1, 6, 3, 5, 8, 7, 9, 0]
    self.assertEqual(expected_two_epochs, actual_values)

  def test_mixing_zero_one_probability_fails_with_error(self):
    with self.assertRaises(ValueError):
      _ = mix.MixedLazyIterDataset(
          parents=[self.even_ds, self.odd_ds], proportions=[0, 1]
      )

  def test_mix_infinite_datasets(self):
    zeros = lazy_dataset.RangeLazyMapDataset(0, 1).repeat()
    ones = lazy_dataset.RangeLazyMapDataset(1, 2).repeat()
    self.assertLen(zeros, sys.maxsize)
    self.assertLen(ones, sys.maxsize)
    ld = mix.MixedLazyIterDataset(
        [zeros.to_iter_dataset(), ones.to_iter_dataset()], proportions=[4, 1]
    )
    # Mix again.
    ld = mix.MixedLazyIterDataset(
        [ld, ones.to_iter_dataset()], proportions=[1, 1]
    )
    ld_iter = iter(ld)
    num_samples = 1000
    value_counts = np.bincount(
        [next(ld_iter) for _ in range(num_samples)]
    ).tolist()
    self.assertEqual(value_counts, [400, 600])

  def test_checkpointing(self):
    ds = mix.MixedLazyIterDataset(
        parents=[self.even_ds, self.odd_ds], proportions=[1, 1]
    )
    ds_iter = iter(ds)

    max_steps = 10
    values_without_interruption = []
    checkpoints = []

    for _ in range(max_steps):
      checkpoints.append(ds_iter.get_state())  # pytype: disable=attribute-error
      values_without_interruption.append(next(ds_iter))

    for starting_step in [0, 1, 5, 8]:
      ds_iter.set_state(checkpoints[starting_step])  # pytype: disable=attribute-error
      for i in range(starting_step, max_steps):
        np.testing.assert_array_equal(
            next(ds_iter), values_without_interruption[i]
        )


if __name__ == "__main__":
  absltest.main()
