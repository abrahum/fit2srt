from datetime import datetime, timezone
from garmin_fit_sdk import Decoder, Stream
from typing import Iterable, Optional
from pydantic import BaseModel
from srt import Subtitle, compose


class Record(BaseModel):
    timestamp: datetime
    postion_lat: Optional[int] = None
    postion_long: Optional[int] = None
    distance: float
    altitude: float  # 海拔
    speed: float
    heart_rate: int
    cadence: int
    temperature: int
    enhanced_speed: float
    enhanced_altitude: Optional[float] = None

    def sub_content(self, speed: float = None) -> str:
        return f"速度:{ speed if speed else self.speed * 3.6:4.1f} \n海拔:{0 if self.altitude > 8000.0 else self.altitude:4.0f}\n心率:{self.heart_rate:4.0f}"


def records_generator(data: list[dict]):
    for r in data:
        yield Record(**r)


class Event(BaseModel):
    timestamp: datetime
    event: str
    event_type: str


def events_generator(data: list[dict]):
    for r in data:
        yield Event(**r)


def read_fit(file_path: str) -> tuple[Iterable[Event], Iterable[Record]]:
    stream = Stream.from_file(file_path)
    decoder = Decoder(stream)
    messages, _ = decoder.read()  # todo
    return (
        events_generator(messages["event_mesgs"]),
        records_generator(messages["record_mesgs"]),
    )


def until_stop_event(events: Iterable[Event]) -> Optional[Event]:
    for event in events:
        if event.event == "timer":  # and event.event_type == "stop":
            return event
    return None


def subtitle_generator(
    events: Iterable[Event],
    records: Iterable[Record],
    start_time: Optional[datetime] = None,
) -> Iterable[Subtitle]:
    index = 1
    if not start_time:
        start_time = next(events).timestamp
    temp_record: Record = next(records)
    # stop_event = until_stop_event(events)
    for record in records:
        # if stop_event and record.timestamp > stop_event.timestamp:
        #     yield Subtitle(
        #         index,
        #         start=temp_record.timestamp - start_time,
        #         end=stop_event.timestamp - start_time,
        #         content=temp_record.sub_content(),
        #     )
        #     index += 1
        #     yield Subtitle(
        #         index,
        #         start=stop_event.timestamp - start_time,
        #         end=record.timestamp - start_time,
        #         content=temp_record.sub_content(speed=0.0),
        #     )
        #     stop_event = until_stop_event(events)
        # else:
        if record.timestamp < start_time:
            temp_record = record
            continue
        yield Subtitle(
            index,
            start=temp_record.timestamp - start_time,
            end=record.timestamp - start_time,
            content=temp_record.sub_content(),
        )
        index += 1
        temp_record = record


if __name__ == "__main__":
    events, records = read_fit("test2.fit")
    with open("test3.srt", "w", encoding="utf-8") as f:
        f.write(
            compose(
                subtitle_generator(
                    events,
                    records,
                    start_time=datetime(2024, 5, 25, 7, 12, tzinfo=timezone.utc),
                )
            )
        )
