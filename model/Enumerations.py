class UserRight:

    def __init__(self):
        pass

    role_management = "role_management"
    land_office_admin = "land_office_administration"
    cadastre_view = "cadastre_view"
    cadastre_update = "cadastre_update"
    contracting_view = "contracting_view"
    contracting_update = "contracting_update"
    reporting = "reporting"
    application_update = "application_update"
    application_view = "application_view"


class ApplicationType:

    def __init__(self):
        pass

    privatization = 1  # r
    giving_up_ownership = 2  # r
    privatization_representation = 3  # r
    buisness_from_state = 4  # r
    possession_right = 5  # c
    use_right = 6  # c
    transfer_possession_right = 7  # c
    mortgage_possession = 8  # c
    change_land_use = 9  # c
    extension_possession = 10  # c
    possession_right_use_right = 11  # c
    reissue_possession_use_right = 12  # c
    change_of_area = 13  # c
    encroachment = 14  # c
    change_ownership = 15  # r
    auctioning_owner = 16
    auctioning_possess = 17
    auctioning_use = 18
    special_use = 22

class PersonType:

    def __init__(self):
        pass

    legally_capable_mongolian = 10
    legally_uncapable_mongolian = 20
    mongolian_buisness = 30
    mongolian_state_org = 40
    foreign_citizen = 50
    legal_entity_foreign = 60

