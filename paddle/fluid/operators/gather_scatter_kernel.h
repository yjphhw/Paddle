/* Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */

#include "paddle/fluid/framework/tensor.h"
#include "paddle/fluid/platform/device_context.h"
#include "paddle/fluid/platform/float16.h"

#pragma once

namespace paddle {
namespace operators {

#define Instantiate_Template_Function(func)                                  \
  Instantiate_Template_Function_index_t(                                     \
      func, int) Instantiate_Template_Function_index_t(func, float)          \
      Instantiate_Template_Function_index_t(func, double)                    \
          Instantiate_Template_Function_index_t(func, int64_t)               \
              Instantiate_Template_Function_index_t(func, platform::float16) \
                  Instantiate_Template_Function_index_t(func, unsigned char)

#define Instantiate_Template_Function_index_t(func, tensor_t)            \
  template void func<tensor_t, int>(phi::DenseTensor input,              \
                                    int dim,                             \
                                    const phi::DenseTensor& index,       \
                                    phi::DenseTensor result,             \
                                    const platform::DeviceContext& ctx); \
  template void func<tensor_t, int64_t>(phi::DenseTensor input,          \
                                        int dim,                         \
                                        const phi::DenseTensor& index,   \
                                        phi::DenseTensor result,         \
                                        const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void cpu_gather_kernel(phi::DenseTensor self,
                       int dim,
                       const phi::DenseTensor& index,
                       phi::DenseTensor result,
                       const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void cpu_scatter_assign_kernel(phi::DenseTensor self,
                               int dim,
                               const phi::DenseTensor& index,
                               phi::DenseTensor src,
                               const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void cpu_scatter_add_kernel(phi::DenseTensor self,
                            int dim,
                            const phi::DenseTensor& index,
                            phi::DenseTensor src,
                            const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void cpu_scatter_mul_kernel(phi::DenseTensor self,
                            int dim,
                            const phi::DenseTensor& index,
                            phi::DenseTensor src,
                            const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void cpu_scatter_input_grad_kernel(phi::DenseTensor self,
                                   int dim,
                                   const phi::DenseTensor& index,
                                   phi::DenseTensor result,
                                   const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void gpu_gather_kernel(phi::DenseTensor self,
                       int dim,
                       const phi::DenseTensor& index,
                       phi::DenseTensor result,
                       const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void gpu_scatter_assign_kernel(phi::DenseTensor self,
                               int dim,
                               const phi::DenseTensor& index,
                               phi::DenseTensor src,
                               const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void gpu_scatter_add_kernel(phi::DenseTensor self,
                            int dim,
                            const phi::DenseTensor& index,
                            phi::DenseTensor src,
                            const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void gpu_scatter_mul_kernel(phi::DenseTensor self,
                            int dim,
                            const phi::DenseTensor& index,
                            phi::DenseTensor src,
                            const platform::DeviceContext& ctx);

template <typename tensor_t, typename index_t>
void gpu_scatter_input_grad_kernel(phi::DenseTensor self,
                                   int dim,
                                   const phi::DenseTensor& index,
                                   phi::DenseTensor result,
                                   const platform::DeviceContext& ctx);
}  // namespace operators
}  // namespace paddle
