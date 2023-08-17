import instagrapi
import instagrapi.types
from app.api.instagram.models.database import User

# from app.api.instagram.models.schemas import User, UserCnfg, UserData
from app.core.packages.celery_app import celery_app
from celery import current_task


@celery_app.task()
def follow_likers(user: User):
    session = user.login()
    account_usernames = list((cnfg := UserCnfg(**user.usercnfg)).farms.keys())
    amount = cnfg.interaction_session_limit
    quality = cnfg.quality
    followers = (data := UserData(**user.userdata)).followers
    followed = data.following

    def getMedia() -> instagrapi.types.Media:
        potential_media: list[instagrapi.types.Media] = [
            session.user_medias(session.user_id_from_username(name), 1)[0]
            for name in account_usernames
        ]

        potential_media.sort(key=lambda x: x.taken_at)
        return potential_media[0]

    media_scouted = getMedia()

    people_followed: list[int] = []
    people_ignored: list[int] = []
    while len(people_followed) < amount:
        people = session.media_likers(media_scouted.id)
        for person in people:
            if len(people_followed) >= amount:
                break  # limit re-check
            to_follow = all(
                [
                    int(person.pk) not in l
                    for l in (followers, followed, people_followed, people_ignored)
                ]
            )
            # checks for bot accounts
            if person.is_private:
                to_follow = False
            if len([char for char in person.username if char.isnumeric()]) >= 3:
                to_follow = False
            if quality and to_follow:
                # quality checks
                person = session.user_info(person.pk, True)
                if person.following_count >= 350:
                    to_follow = False
                    # follow
            if to_follow:
                people_followed.append(int(person.pk)) if session.user_follow(
                    person.pk
                ) else None
            else:
                people_ignored.append(int(person.pk))
            to_follow = False
            current_task.update_state(
                state="PROGRESS",
                meta={"process_percent": (len(people_followed) / amount) * 100},
            )

    user.userdata["following"].append(people_followed)
    user.save()


@celery_app.task()
def unfollow_users(user: User):
    session = user.login()
    peopleid: list[int] = user.userdata["following"][
        : user.usercnfg["interation_session_limit"] :
    ]
    people_unfollowed = [
        personid for personid in peopleid if session.user_unfollow(str(personid))
    ]
    for people in people_unfollowed:
        user.userdata["following"].remove(people)
    user.save()


@celery_app.task()  # subtask -> database
def get_followers(
    session: instagrapi.Client, username: str, amount: int, endcursor: str
):
    userid = session.user_id_from_username(username)
    followers, end = session.user_followers_gql_chunk(userid, amount, endcursor)
    user_followers = [int(usershort.pk) for usershort in followers]
    return user_followers, end


@celery_app.task()  # subtask -> database
def get_following(session: instagrapi.Client, username: str) -> list[int]:
    userid = session.user_id_from_username(username)
    return [int(userid) for userid, _ in session.user_following(userid)]
