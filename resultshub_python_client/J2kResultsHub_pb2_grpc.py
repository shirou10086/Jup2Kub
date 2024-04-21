# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import J2kResultsHub_pb2 as J2kResultsHub__pb2


class ResultsHubStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ClaimCellFinished = channel.unary_unary(
                '/J2KResultsHub.ResultsHub/ClaimCellFinished',
                request_serializer=J2kResultsHub__pb2.VarResults.SerializeToString,
                response_deserializer=J2kResultsHub__pb2.Empty.FromString,
                )
        self.FetchVarResult = channel.unary_unary(
                '/J2KResultsHub.ResultsHub/FetchVarResult',
                request_serializer=J2kResultsHub__pb2.FetchVarResultRequest.SerializeToString,
                response_deserializer=J2kResultsHub__pb2.VarResult.FromString,
                )
        self.RequiringFile = channel.unary_unary(
                '/J2KResultsHub.ResultsHub/RequiringFile',
                request_serializer=J2kResultsHub__pb2.FileReqeust.SerializeToString,
                response_deserializer=J2kResultsHub__pb2.Empty.FromString,
                )
        self.SayHello = channel.unary_unary(
                '/J2KResultsHub.ResultsHub/SayHello',
                request_serializer=J2kResultsHub__pb2.HelloRequest.SerializeToString,
                response_deserializer=J2kResultsHub__pb2.HelloReply.FromString,
                )


class ResultsHubServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ClaimCellFinished(self, request, context):
        """NOTE: for those rpcs, if the call fails, the pod should retry, 
        the call will eventually success when ResultsHub recovers
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FetchVarResult(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequiringFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayHello(self, request, context):
        """The Ping-Pong service for cluster testing, remove in future
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ResultsHubServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ClaimCellFinished': grpc.unary_unary_rpc_method_handler(
                    servicer.ClaimCellFinished,
                    request_deserializer=J2kResultsHub__pb2.VarResults.FromString,
                    response_serializer=J2kResultsHub__pb2.Empty.SerializeToString,
            ),
            'FetchVarResult': grpc.unary_unary_rpc_method_handler(
                    servicer.FetchVarResult,
                    request_deserializer=J2kResultsHub__pb2.FetchVarResultRequest.FromString,
                    response_serializer=J2kResultsHub__pb2.VarResult.SerializeToString,
            ),
            'RequiringFile': grpc.unary_unary_rpc_method_handler(
                    servicer.RequiringFile,
                    request_deserializer=J2kResultsHub__pb2.FileReqeust.FromString,
                    response_serializer=J2kResultsHub__pb2.Empty.SerializeToString,
            ),
            'SayHello': grpc.unary_unary_rpc_method_handler(
                    servicer.SayHello,
                    request_deserializer=J2kResultsHub__pb2.HelloRequest.FromString,
                    response_serializer=J2kResultsHub__pb2.HelloReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'J2KResultsHub.ResultsHub', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ResultsHub(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ClaimCellFinished(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/J2KResultsHub.ResultsHub/ClaimCellFinished',
            J2kResultsHub__pb2.VarResults.SerializeToString,
            J2kResultsHub__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def FetchVarResult(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/J2KResultsHub.ResultsHub/FetchVarResult',
            J2kResultsHub__pb2.FetchVarResultRequest.SerializeToString,
            J2kResultsHub__pb2.VarResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequiringFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/J2KResultsHub.ResultsHub/RequiringFile',
            J2kResultsHub__pb2.FileReqeust.SerializeToString,
            J2kResultsHub__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SayHello(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/J2KResultsHub.ResultsHub/SayHello',
            J2kResultsHub__pb2.HelloRequest.SerializeToString,
            J2kResultsHub__pb2.HelloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
