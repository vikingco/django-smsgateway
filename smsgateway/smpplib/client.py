#
# smpplib -- SMPP Library for Python
# Copyright (c) 2005 Martynas Jocius <mjoc@akl.lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's

"""SMPP client module"""
from logging import getLogger

from socket import socket, AF_INET, SOCK_STREAM, error as socket_error, timeout
from struct import unpack, error as struct_error
from binascii import b2a_hex

from smpp import make_pdu, parse_pdu
from pdu import descs, SMPP_ESME_RINVBNDSTS, PDU


SMPP_CLIENT_STATE_CLOSED = 0
SMPP_CLIENT_STATE_OPEN = 1
SMPP_CLIENT_STATE_BOUND_TX = 2
SMPP_CLIENT_STATE_BOUND_RX = 3
SMPP_CLIENT_STATE_BOUND_TRX = 4

logger = getLogger(__name__)

command_states = {
    'bind_transmitter': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transmitter_resp': (SMPP_CLIENT_STATE_OPEN,),
    'bind_receiver': (SMPP_CLIENT_STATE_OPEN,),
    'bind_receiver_resp': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transceiver': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transceiver_resp': (SMPP_CLIENT_STATE_OPEN,),
    'outbind': (SMPP_CLIENT_STATE_OPEN,),
    'unbind': (SMPP_CLIENT_STATE_BOUND_TX,
               SMPP_CLIENT_STATE_BOUND_RX,
               SMPP_CLIENT_STATE_BOUND_TRX,),
    'unbind_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                    SMPP_CLIENT_STATE_BOUND_RX,
                    SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm': (SMPP_CLIENT_STATE_BOUND_TX,
                  SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                       SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_multi': (SMPP_CLIENT_STATE_BOUND_TX,
                        SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_multi_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                             SMPP_CLIENT_STATE_BOUND_TRX,),
    'data_sm': (SMPP_CLIENT_STATE_BOUND_TX,
                SMPP_CLIENT_STATE_BOUND_RX,
                SMPP_CLIENT_STATE_BOUND_TRX,),
    'data_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,),
    'deliver_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                   SMPP_CLIENT_STATE_BOUND_TRX,),
    'deliver_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                        SMPP_CLIENT_STATE_BOUND_TRX,),
    'query_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                 SMPP_CLIENT_STATE_BOUND_TRX,),
    'query_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                      SMPP_CLIENT_STATE_BOUND_TRX,),
    'cancel_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                  SMPP_CLIENT_STATE_BOUND_TRX,),
    'cancel_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                       SMPP_CLIENT_STATE_BOUND_TRX,),
    'replace_sm': (SMPP_CLIENT_STATE_BOUND_TX,),
    'replace_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,),
    'enquire_link': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,),
    'enquire_link_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                          SMPP_CLIENT_STATE_BOUND_RX,
                          SMPP_CLIENT_STATE_BOUND_TRX,),
    'alert_notification': (SMPP_CLIENT_STATE_BOUND_RX,
                           SMPP_CLIENT_STATE_BOUND_TRX,),
    'generic_nack': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,)
}

state_setters = {
    'bind_transmitter_resp': SMPP_CLIENT_STATE_BOUND_TX,
    'bind_receiver_resp': SMPP_CLIENT_STATE_BOUND_RX,
    'bind_transceiver_resp': SMPP_CLIENT_STATE_BOUND_TRX,
    'unbind_resp': SMPP_CLIENT_STATE_OPEN
}

#
# Global response number
#
responses = 0


def log(*msg):
    """Log message"""

    msg = map(str, msg)


class Client:
    """SMPP client class"""

    state = SMPP_CLIENT_STATE_CLOSED

    host = None
    port = None
    vendor = None
    _socket = None

    _stack = []  # PDU stack
    _error_stack = None

    def __init__(self, host, port):
        """Initialize"""

        self.host = host
        self.port = int(port)
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(5)
        self._error_stack = []
        self.receiver_mode = False

    def connect(self):
        """Connect to SMSC"""

        try:
            self._socket.connect((self.host, self.port))
            self.state = SMPP_CLIENT_STATE_OPEN
        except socket_error:
            raise ConnectionError('Connection refused')

    def disconnect(self):
        """Disconnect from the SMSC"""

        logger.debug('Disconnecting...')

        self._socket.close()
        self.state = SMPP_CLIENT_STATE_CLOSED

    def _bind(self, command_name, **args):
        """Send bind_transmitter command to the SMSC"""

        if command_name in ['bind_receiver', 'bind_transceiver']:
            logger.debug('I am receiver')
            self.receiver_mode = True

        p = make_pdu(command_name, **(args))

        self.send_pdu(p)
        return self.read_pdu()

    def bind_transmitter(self, **args):
        """Bind as a transmitter"""

        return self._bind('bind_transmitter', **(args))

    def bind_receiver(self, **args):
        """Bind as a receiver"""

        return self._bind('bind_receiver', **(args))

    def bind_transceiver(self, **args):
        """Bind as a transmitter and receiver at once"""

        return self._bind('bind_transceiver', **(args))

    def unbind(self):
        """Unbind from the SMSC"""

        p = make_pdu('unbind')

        self.send_pdu(p)
        return self.read_pdu()

    def send_pdu(self, p):
        """Send PDU to the SMSC"""

        if self.state not in command_states[p.command]:
            raise Exception('Command {} failed: {}'.format(p.command, descs[SMPP_ESME_RINVBNDSTS]))

        self._push_pdu(p)

        generated = p.generate()

        logger.debug(' '.join(
                [str(x) for x in ['>>', b2a_hex(generated), len(generated), 'bytes']]))

        self._socket.send(generated)

        return True

    def read_pdu(self):
        """Read PDU from the SMSC"""

        logger.debug('Waiting for PDU...')

        raw_len = self._socket.recv(4)
        if raw_len == 0:
            return False

        try:
            length = unpack('>L', raw_len)[0]
        except struct_error:
            logger.debug('Receive broken pdu...')
            return False
        raw_pdu = self._socket.recv(length - 4)
        raw_pdu = raw_len + raw_pdu

        logger.debug(' '.join(
                [str(x) for x in ['<<', b2a_hex(raw_pdu), len(raw_pdu), 'bytes']]))

        PDU.extract_command(raw_pdu)

        p = parse_pdu(raw_pdu)
        self._push_pdu(p)

        if p.is_error():
            raise Exception('({}) {}: {}'.format(p.status, p.command, descs[p.status]))
        elif p.command in state_setters.keys():
            self.state = state_setters[p.command]

        return p

    def accept(self, object):
        """Accept an object"""

        raise NotImplementedError('not implemented')

    def _message_received(self, p):
        """Handler for received message event"""
        dsmr = make_pdu('deliver_sm_resp')
        dsmr.sequence = p.sequence
        self.send_pdu(dsmr)
        return self.message_received_handler(pdu=p)

    def _enquire_link_received(self):
        ler = make_pdu('enquire_link_resp')
        self.send_pdu(ler)
        logger.debug('Link Enuiry...')

    def set_message_received_handler(self, func):
        """Set new function to handle message receive event"""

        self.message_received_handler = func

    @staticmethod
    def message_received_handler(**args):
        """Custom handler to process received message. May be overridden"""

        logger.debug('Message received handler (shoud be overridden)')

    def listen(self):
        """Listen for PDUs and act"""

        if not self.receiver_mode:
            raise Exception('Client.listen() is not allowed to be invoked manually for non receiver connection')

        while True:
            try:
                p = self.read_pdu()
            except timeout:
                logger.debug('Socket timeout, listening again')
                continue

            if p.command == 'unbind':
                break
            elif p.command == 'deliver_sm':
                keep_listening = self._message_received(p)
                if not keep_listening:
                    break
            elif p.command == 'enquire_link':
                self._enquire_link_received()

    def send_message(self, **args):
        """Send message

        Required Arguments:
            source_addr_ton -- Source address TON
            source_addr -- Source address (string)
            dest_addr_ton -- Destination address TON
            destination_addr -- Destination address (string)
            short_message -- Message text (string)"""

        ssm = make_pdu('submit_sm', **(args))

        self.send_pdu(ssm)
        resp = self.read_pdu()

        return resp

    def _push_pdu(self, p):
        """Push PDU into a stack"""

        if p.is_request():
            k = 'request'
        else:
            k = 'response'

        self._stack.append({p.sequence: {k: p}})


class ConnectionError(Exception):
    """Connection error"""


#
# Main block for testing
#
if __name__ == '__main__':

    from sys import path
    path.insert(0, '..')
    from smpplib import client as smpplib_client

    def recv_handler(**args):
        pass

    client = smpplib_client.Client('localhost', 2775)
    client.connect()

    client.set_message_received_handler(recv_handler)

    try:
        client.bind_transceiver(system_id='smppclient1', password='pwd1', system_type='www')
        client.listen()
    finally:
        client.unbind()
        client.disconnect()
