from __future__ import annotations

from game.roles import Role


def distribute_roles(count: int) -> list[Role]:
    """Подбор ролей по числу игроков (4–20)."""
    if count < 4:
        raise ValueError("Нужно минимум 4 игрока")
    if count > 20:
        raise ValueError("Максимум 20 игроков")

    roles: list[Role] = [Role.DON, Role.COMMISSIONER, Role.DOCTOR]

    if count >= 5:
        roles.append(Role.MAFIA)
    if count >= 6:
        roles.append(Role.SERGEANT)
    if count >= 7:
        roles.append(Role.MANIAC)
    if count >= 8:
        roles.append(Role.MISTRESS)
    if count >= 9:
        roles.append(Role.HOMELESS)
    if count >= 10:
        roles.append(Role.LAWYER)
    if count >= 11:
        roles.append(Role.LUCKY)
    if count >= 12:
        roles.append(Role.KAMIKAZE)
    if count >= 13:
        roles.append(Role.SUICIDE)
    if count >= 14:
        roles.append(Role.MAFIA)
    if count >= 16:
        roles.append(Role.MAFIA)
    if count >= 18:
        roles.append(Role.MAFIA)

    while len(roles) < count:
        roles.append(Role.CIVILIAN)

    return roles[:count]
