"""Launch the GUI-first ASW MVP against a local journal."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from asw.agent_api import LocalAgentServer
from asw.defaults import mvp_policy
from asw.delivery import WindowsAppSdkDelivery, WindowsAppSdkSender
from asw.gui import launch
from asw.service import ASWService
from asw.sources import WindowsObservationRuntime


def run() -> None:
    service = ASWService(root / "data" / "asw.journal.jsonl", mvp_policy())
    windows_sender = WindowsAppSdkSender()
    service.windows_delivery = WindowsAppSdkDelivery(service, windows_sender)
    agent_server = LocalAgentServer(service)
    agent_server.start()
    observation_runtime = WindowsObservationRuntime(service)
    observation_runtime.start()
    try:
        launch(service, agent_server)
    finally:
        observation_runtime.stop()
        agent_server.stop()
        windows_sender.close()


if __name__ == "__main__":
    run()
