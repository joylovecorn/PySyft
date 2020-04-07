from syft.generic.tensor import AbstractTensor
from syft.generic.frameworks.hook import hook_args
from syft.generic.frameworks.overload import overloaded
from syft.workers.abstract import AbstractWorker
from syft.frameworks.tenseal import ckks_vector
import syft as sy
import torch as th


class CKKSTensor(AbstractTensor):
    def __init__(self, owner=None, id=None, tags=None, description=None):
        """Initializes a CKKSTensor, whose behaviour is to encrypt a tensor
        with CKKS homomorphic encryption scheme.

        Args:
            owner: An optional BaseWorker object to specify the worker on which
                the tensor is located.
            id: An optional string or integer id of the CKKSTensor.
            tags: an optional set of hashtags corresponding to this tensor
                which this tensor should be searchable for
            description: an optional string describing the purpose of the
                tensor
        """
        super().__init__(id=id, owner=owner, tags=tags, description=description)

    def encrypt(self, context, scale):
        """This method will encrypt each value in the tensor using CKKS
        homomorphic encryption.

        Args:
            context: a TenSEALContext created using 
                syft.frameworks.torch.he.tenseal.context()
            scale: the scale to be used to encode tensor values.
        """

        output = CKKSTensor().on(self.child)
        output.child.encrypt_(context)
        return output

    def encrypt_(self, context, scale):
        """This method will encrypt the whole tensor using CKKS
        homomorphic encryption.

        Args:
            context: a TenSEALContext created using 
                syft.frameworks.torch.he.tenseal.context()
            scale: the scale to be used to encode tensor values.
        """
        # can only encrypts vectors
        self._shape = self.child.shape
        vector = self.child.flatten().tolist()
        self.child = ckks_vector(context, scale, vector)

    def decrypt(self, secret_key=None):
        """This method will decrypt the tensor, returning a normal
        torch tensor.

        Args:
            secret_key: optional if the tensor was created in 
                the current context. Used to decrypt the tensor.
        """
        if secret_key is None:
            x_decrypted = self.child.decrypt()
        else:
            x_decrypted = self.child.decrypt(secret_key)

        # restor original shape
        x = th.tensor(x_decrypted)
        return x.reshape(self._shape)
