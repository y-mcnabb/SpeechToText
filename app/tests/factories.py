from factory import Factory, Sequence, SubFactory, Faker

from app.models.session import User, Session, AudioData


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


class UserFactory(Factory):
    class Meta:
        model = User

    id_ = Faker("pystr")
    session = SubFactory(SessionFactory)
