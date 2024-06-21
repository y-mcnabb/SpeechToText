from factory import Factory, Faker, LazyAttribute, SubFactory

from app.models.session import AudioData, Session, User


class AudioDataFactory(Factory):
    class Meta:
        model = AudioData

    name = Faker("pystr")
    duration = Faker("pyfloat")
    size = Faker("pyint")
    type = Faker("pystr")


class SessionFactory(Factory):
    class Meta:
        model = Session

    audio = SubFactory(AudioDataFactory)
    transcript_file = LazyAttribute(
        lambda p: "{} {}".format(Faker("pystr"), Faker("pystr"))
    )


class UserFactory(Factory):
    class Meta:
        model = User

    id_ = Faker("pystr")
    session = SubFactory(SessionFactory)
