"""Launch the GUI-first ASW MVP against a local journal."""
from pathlib import Path

from asw.agent_api import LocalAgentServer
from asw.defaults import mvp_policy
from asw.delivery import WindowsAppSdkDelivery, WindowsAppSdkSender
from asw.gui import launch
from asw.service import ASWService
from asw.sources import WindowsObservationRuntime

root = Path(__file__).resolve().parent


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
