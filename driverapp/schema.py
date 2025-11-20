import strawberry_django
from strawberry import auto
import strawberry
import asyncio



from accounts.models import CustomUser, DriverProfile

@strawberry_django.type(CustomUser)
class UserType:
    id: auto
    name: auto
    email: auto
    driver_profile: "DriverProfileType | None"


@strawberry_django.type(DriverProfile)
class DriverProfileType:
    id: auto
    driver: UserType
    profile_picture: auto


@strawberry.type
class Query:
    users: list[UserType] = strawberry_django.field()

# server part
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def users_online(self) -> list[UserType]:
        while True:
            online_users = User.objects.filter(is_online=True)
            yield online_users
            asyncio.sleep(1)

schema = strawberry.Schema(
    query=Query,
)