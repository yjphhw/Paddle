#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import pickle

import numpy as np

import paddle
import paddle.distributed as dist
import paddle.distributed.communication.stream as stream
import paddle.fluid.framework as framework


def all_gather(tensor_list, tensor, group=None, sync_op=True):
    """

    Gather tensors from all participators and all get the result. As shown
    below, one process is started with a GPU and the data of this process is represented
    by its group rank. Through the all_gather operator, each GPU will have data
    from all GPUs.

    .. image:: https://githubraw.cdn.bcebos.com/PaddlePaddle/docs/develop/docs/api/paddle/distributed/img/allgather.png
        :width: 800
        :alt: all_gather
        :align: center

    Args:
        tensor_list (list): A list of output Tensors. Every element in the list must be a Tensor whose data type
            should be float16, float32, float64, int32, int64, int8, uint8, bool or bfloat16.
        tensor (Tensor): The Tensor to send. Its data type
            should be float16, float32, float64, int32, int64, int8, uint8, bool or bfloat16.
        group (Group, optional): The group instance return by new_group or None for global default group.
        sync_op (bool, optional): Whether this op is a sync op. The default value is True.

    Returns:
        None.

    Examples:
        .. code-block:: python

            # required: distributed
            import paddle
            import paddle.distributed as dist

            dist.init_parallel_env()
            tensor_list = []
            if dist.get_rank() == 0:
                data = paddle.to_tensor([[4, 5, 6], [4, 5, 6]])
            else:
                data = paddle.to_tensor([[1, 2, 3], [1, 2, 3]])
            dist.all_gather(tensor_list, data)
            print(tensor_list)
            # [[[4, 5, 6], [4, 5, 6]], [[1, 2, 3], [1, 2, 3]]] (2 GPUs)
    """
    if not framework._in_legacy_dygraph():
        return stream.all_gather(tensor_list, tensor, group, sync_op)

    # NOTE: uncomment code below when having fully complex support
    # def convert_to_complex(list_of_tensor):
    #     list_of_complex = []
    #     for tensor in list_of_tensor:
    #         list_of_complex.append(paddle.as_complex(tensor))
    #     return list_of_complex

    # is_input_complex = (tensor.dtype == paddle.complex64
    #                     or tensor.dtype == paddle.complex128)
    # if is_input_complex:
    #     tensor = paddle.as_real(tensor)

    # code below will be removed after we remove the old dygraph
    if group is not None and not group.is_member():
        return

    ring_id = 0 if group is None else group.id
    nranks = dist.get_world_size()
    out = paddle._legacy_C_ops.c_allgather(
        tensor,
        'use_calc_stream',
        sync_op,
        'ring_id',
        ring_id,
        'nranks',
        nranks,
    )
    tensor_list.clear()
    tensor_list.extend(paddle.split(out, nranks, 0))


def _convert_object_to_tensor(obj):
    _pickler = pickle.Pickler
    f = io.BytesIO()
    _pickler(f).dump(obj)
    data = np.frombuffer(f.getvalue(), dtype=np.uint8)
    tensor = paddle.to_tensor(data)
    return tensor, tensor.numel()


def _convert_tensor_to_object(tensor, len_of_tensor):
    _unpickler = pickle.Unpickler
    return _unpickler(io.BytesIO(tensor.numpy()[:len_of_tensor])).load()


def all_gather_object(object_list, obj, group=None):
    """

    Gather picklable objects from all participators and all get the result. Similiar to all_gather(), but python object can be passed in.

    Args:
        object_list (list): A list of output object. The datatype of every element in the list is same as the input obj.
        obj (Any): The picklable object to send.
        group (Group): The group instance return by new_group or None for global default group.

    Returns:
        None.

    Warning:
        This API only supports the dygraph mode.

    Examples:
        .. code-block:: python

            # required: distributed
            import paddle
            import paddle.distributed as dist

            dist.init_parallel_env()
            object_list = []
            if dist.get_rank() == 0:
                obj = {"foo": [1, 2, 3]}
            else:
                obj = {"bar": [4, 5, 6]}
            dist.all_gather_object(object_list, obj)
            print(object_list)
            # [{'foo': [1, 2, 3]}, {'bar': [4, 5, 6]}] (2 GPUs)
    """
    assert (
        framework.in_dygraph_mode()
    ), "all_gather_object doesn't support static graph mode."

    tensor, len_of_tensor = _convert_object_to_tensor(obj)

    # gather len_of_tensor from all ranks
    list_len_of_tensor = []
    all_gather(list_len_of_tensor, len_of_tensor, group)
    # get the max length from list
    max_len_of_tensor = int(max(list_len_of_tensor).item())
    # resize the input tensor to max length avoid hang in all gather
    # Note(liyurui): Maybe we should support various length all_gather?
    # Now this operation is efficient for we don't support resize in python.
    numpy_data = tensor.numpy()
    numpy_data = np.resize(numpy_data, [max_len_of_tensor])
    input_tensor = paddle.to_tensor(numpy_data)

    tensor_list = []
    all_gather(tensor_list, input_tensor, group)
    for i, tensor in enumerate(tensor_list):
        object_list.append(
            _convert_tensor_to_object(tensor, list_len_of_tensor[i])
        )
