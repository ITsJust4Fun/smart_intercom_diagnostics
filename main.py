import logging
import asyncio
import grpc
import psutil

import diagnostics_pb2
import diagnostics_pb2_grpc


class Diagnostics(diagnostics_pb2_grpc.DiagnosticsServicer):

    async def GetDiagnostic(
            self, request: diagnostics_pb2.Empty,
            context: grpc.aio.ServicerContext) -> diagnostics_pb2.Diagnostic:

        hdd = psutil.disk_usage('.')
        cpu = psutil.cpu_percent(interval=None)
        virtual_memory = psutil.virtual_memory()

        return diagnostics_pb2.Diagnostic(
            cpu=cpu,
            freeRAM=virtual_memory.free / (2 ** 30),
            usedRAM=virtual_memory.used / (2 ** 30),
            totalRAM=virtual_memory.total / (2 ** 30),
            freeHDD=hdd.free / (2 ** 30),
            usedHDD=hdd.used / (2 ** 30),
            totalHDD=hdd.total / (2 ** 30)
        )


async def serve() -> None:
    server = grpc.aio.server()
    diagnostics_pb2_grpc.add_DiagnosticsServicer_to_server(Diagnostics(), server)
    listen_addr = 'localhost:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
