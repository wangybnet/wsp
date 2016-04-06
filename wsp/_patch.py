# coding=utf-8

import socket
from asyncio.base_events import BaseEventLoop
from asyncio.coroutines import coroutine
from asyncio.base_events import tasks
import struct


@coroutine
def create_connection(self, protocol_factory, host=None, port=None, *,
                      ssl=None, family=0, proto=0, flags=0, sock=None,
                      local_addr=None, server_hostname=None):
    """Connect to a TCP server.

    Create a streaming transport connection to a given Internet host and
    port: socket family AF_INET or socket.AF_INET6 depending on host (or
    family if specified), socket type SOCK_STREAM. protocol_factory must be
    a callable returning a protocol instance.

    This method is a coroutine which will try to establish the connection
    in the background.  When successful, the coroutine returns a
    (transport, protocol) pair.
    """
    if server_hostname is not None and not ssl:
        raise ValueError('server_hostname is only meaningful with ssl')

    if server_hostname is None and ssl:
        # Use host as default for server_hostname.  It is an error
        # if host is empty or not set, e.g. when an
        # already-connected socket was passed or when only a port
        # is given.  To avoid this error, you can pass
        # server_hostname='' -- this will bypass the hostname
        # check.  (This also means that if host is a numeric
        # IP/IPv6 address, we will attempt to verify that exact
        # address; this will probably fail, but it is possible to
        # create a certificate for a specific IP address, so we
        # don't judge it here.)
        if not host:
            raise ValueError('You must set server_hostname '
                             'when using ssl without a host')
        server_hostname = host

    if host is not None or port is not None:
        if sock is not None:
            raise ValueError(
                'host/port and sock can not be specified at the same time')

        f1 = self.getaddrinfo(
            host, port, family=family,
            type=socket.SOCK_STREAM, proto=proto, flags=flags)
        fs = [f1]
        if local_addr is not None:
            f2 = self.getaddrinfo(
                *local_addr, family=family,
                type=socket.SOCK_STREAM, proto=proto, flags=flags)
            fs.append(f2)
        else:
            f2 = None

        yield from tasks.wait(fs, loop=self)

        infos = f1.result()
        if not infos:
            raise OSError('getaddrinfo() returned empty list')
        if f2 is not None:
            laddr_infos = f2.result()
            if not laddr_infos:
                raise OSError('getaddrinfo() returned empty list')

        exceptions = []
        for family, type, proto, cname, address in infos:
            try:
                sock = socket.socket(family=family, type=type, proto=proto)
                # --- PATCH ---
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                # -------------
                sock.setblocking(False)
                if f2 is not None:
                    for _, _, _, _, laddr in laddr_infos:
                        try:
                            sock.bind(laddr)
                            break
                        except OSError as exc:
                            exc = OSError(
                                exc.errno, 'error while '
                                'attempting to bind on address '
                                '{!r}: {}'.format(
                                    laddr, exc.strerror.lower()))
                            exceptions.append(exc)
                    else:
                        sock.close()
                        sock = None
                        continue
                yield from self.sock_connect(sock, address)
            except OSError as exc:
                if sock is not None:
                    sock.close()
                exceptions.append(exc)
            except:
                if sock is not None:
                    sock.close()
                raise
            else:
                break
        else:
            if len(exceptions) == 1:
                raise exceptions[0]
            else:
                # If they all have the same str(), raise one.
                model = str(exceptions[0])
                if all(str(exc) == model for exc in exceptions):
                    raise exceptions[0]
                # Raise a combined exception so the user can see all
                # the various error messages.
                raise OSError('Multiple exceptions: {}'.format(
                    ', '.join(str(exc) for exc in exceptions)))

    elif sock is None:
        raise ValueError(
            'host and port was not specified and no sock specified')

    sock.setblocking(False)

    transport, protocol = yield from self._create_connection_transport(
        sock, protocol_factory, ssl, server_hostname)
    return transport, protocol

# Patch it!
BaseEventLoop.create_connection = create_connection
