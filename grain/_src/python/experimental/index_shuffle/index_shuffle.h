/* Copyright 2023 Google LLC. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#ifndef GRAIN_RANDOM_RANDOM_INDEX_SHUFFLE_H_
#define GRAIN_RANDOM_RANDOM_INDEX_SHUFFLE_H_

#include <array>
#include <cstdint>

namespace grain {
namespace random {

// Returns the position of `index` in a permutation of [0, ..., max_index].
//
// Index must be number in [0, ..., max_index].
// Key is the random key for the permutation.
// The returned index will also be in [0, ..., max_index]. For a fixed `key`
// and `max_index` all the possible `index` values and the returned values form
// a bijection.
// Rounds must be a positive even integer >= 4. Larger values improve
// 'randomness' of permutations for small `max_index` values. The time to
// compute the result scales linearly with the number of rounds. We recommend 8
// rounds for a good trade off.
//
// For more details on the algorithm see the top of the cc file.
uint64_t index_shuffle(uint64_t index, uint64_t max_index, uint32_t seed,
                       uint32_t rounds);

}  // namespace random
}  // namespace grain

#endif  // GRAIN_RANDOM_RANDOM_INDEX_SHUFFLE_H_
