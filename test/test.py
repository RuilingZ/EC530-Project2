import pytest
import device_module as dm

db_dir = './ec530_p2.db'

@pytest.mark.parametrize('id, output',
                         [('1', "(1, 'Annie', 'A', 'Male', 'Patient', '9098372839', '1999-10-05', 165, 60)"),
                          ('2', "(2, 'Bob', 'B', 'Male', 'Doctor', '8193748827', '1995-04-02', 180, 80)")])
def test_select_user(id, output):
    conn = dm.create_connection(db_dir)
    user = dm.select_user(conn, id)
    conn.close()
    assert str(user) == output

@pytest.mark.parametrize('fn, ln, gender, role, phone, dob, h, w, output',
                         [('DD', 'D', 'Female', 'Patient', '2222223333', '1999-10-15', 175, 55, 5),
                          ('EE', 'E', 'M', 'Doctor', '3333332222', '1998-11-22', 175, 60, None),
                          ('EE', 'E', 'Male', 'D', '3333332222', '1998-11-22', 175, 60, None)])
def test_insert_user(fn, ln, gender, role, phone, dob, h, w, output):
    conn = dm.create_connection(db_dir)
    last_id = dm.insert_user(conn, fn, ln, gender, role, phone, dob, h, w)
    conn.close()
    assert last_id == output

@pytest.mark.parametrize('id, output',
                         [('6', 0),
                          ('5', 0)])
# output 0 because the auto_increment primary key didn't change in this function

def test_delete_user(id, output):
    conn = dm.create_connection(db_dir)
    last_id = dm.delete_user(conn, id)
    conn.close()
    assert last_id == output

@pytest.mark.parametrize('id, phone, h, w, output',
                         [('4', '1112223333', 180, 72, "(4, 'CC', 'C', 'Male', 'Patient', '1112223333', '2000-11-06', 180, 72)"),
                          ('4', '1111100000', 180, 80, "(4, 'CC', 'C', 'Male', 'Patient', '1111100000', '2000-11-06', 180, 80)"),
                          ('5', '1111100000', 180, 80, 'None')])
def test_update_user(id, phone, h, w, output):
    conn = dm.create_connection(db_dir)
    user = dm.update_user(conn, id, phone, h, w)
    conn.close()
    assert str(user) == output
