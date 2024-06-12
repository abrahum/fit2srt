from garmin_fit_sdk import Decoder, Stream

if __name__ == "__main__":
    stream = Stream.from_file("test2.fit")
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    print(messages.keys())
    print(messages["event_mesgs"][0])
    print(messages["record_mesgs"][0])
