import asyncio
from obci.core.configured_peer import ConfiguredPeer
from obci.core.messages.types import TagMsg, SignalMessage
import time
from obci.core.message_handler_mixin import subscribe_message_handler

__all__ = ('InterfacePeer',)

class InterfacePeer(ConfiguredPeer):

    async def _connections_established(self):
        await super()._connections_established()
        self.create_task(self.random_tags())
        await self.ready()

    async def run_experiment(self):
        while True:
            await asyncio.sleep(5)
            self.send_message(TagMsg(start_timestamp=time.time(), end_timestamp=time.time(), name='dzwiek', channels='-1', desc={'type':'ton1'}))

    @subscribe_message_handler(SignalMessage)
    async def handle_sig(self, msg):
        print(msg)
        print(msg.data.samples)

        
