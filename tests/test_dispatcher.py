from datetime import datetime

from homesec.alerts.dispatcher import AlertDispatcher
from homesec.alerts.events import DetectionEvent


class FakeAlerter:
    def __init__(self):
        self.events = []

    def send(self, event):
        self.events.append(event)


class FailingAlerter:
    def send(self, event):
        raise RuntimeError("boom")


def make_event(source_name="camera1"):
    return DetectionEvent(source_name=source_name, timestamp=datetime.now(), detections=[])


def test_dispatch_sends_to_all_alerters():
    alerter = FakeAlerter()
    dispatcher = AlertDispatcher([alerter], cooldown_seconds=30, clock=lambda: 0.0)

    dispatched = dispatcher.dispatch(make_event())

    assert dispatched is True
    assert len(alerter.events) == 1


def test_dispatch_suppressed_within_cooldown():
    alerter = FakeAlerter()
    clock = {"t": 0.0}
    dispatcher = AlertDispatcher([alerter], cooldown_seconds=30, clock=lambda: clock["t"])

    dispatcher.dispatch(make_event())
    clock["t"] = 10.0
    dispatched_again = dispatcher.dispatch(make_event())

    assert dispatched_again is False
    assert len(alerter.events) == 1


def test_dispatch_allowed_after_cooldown_elapses():
    alerter = FakeAlerter()
    clock = {"t": 0.0}
    dispatcher = AlertDispatcher([alerter], cooldown_seconds=30, clock=lambda: clock["t"])

    dispatcher.dispatch(make_event())
    clock["t"] = 31.0
    dispatched_again = dispatcher.dispatch(make_event())

    assert dispatched_again is True
    assert len(alerter.events) == 2


def test_cooldown_tracked_per_source():
    alerter = FakeAlerter()
    dispatcher = AlertDispatcher([alerter], cooldown_seconds=30, clock=lambda: 0.0)

    dispatcher.dispatch(make_event(source_name="front_door"))
    dispatched_other = dispatcher.dispatch(make_event(source_name="back_yard"))

    assert dispatched_other is True
    assert len(alerter.events) == 2


def test_failing_alerter_does_not_block_others():
    good_alerter = FakeAlerter()
    dispatcher = AlertDispatcher([FailingAlerter(), good_alerter], cooldown_seconds=30)

    dispatcher.dispatch(make_event())

    assert len(good_alerter.events) == 1
