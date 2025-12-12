from attrs import define


@define
class _ToH3:
    pass


class Test1:
    obj = _ToH3()

    def test_h3_upload(self):
        assert 1
