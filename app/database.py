from app import get_db

def query_user(username):
    db = get_db()
    sql = 'SELECT * FROM Users WHERE username=?;'
    cur = db.execute(sql, [username])
    rv = cur.fetchone()
    cur.close()
    db.commit()
    return rv

def query_user_id(uid):
    db = get_db()
    sql = 'SELECT * FROM Users WHERE id=?;'
    cur = db.execute(sql, [uid])
    rv = cur.fetchone()
    cur.close()
    db.commit()
    return rv

def query_friends(u_id):
    db = get_db()
    sql = 'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=? ;'
    cur = db.execute(sql, (u_id, u_id))
    rv = cur.fetchall()
    cur.close()
    db.commit()
    return rv

def query_friend(u_id, username):
    db = get_db()
    sql = 'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=? AND username=? ;'
    cur = db.execute(sql, (u_id, u_id, username))
    rv = cur.fetchone()
    cur.close()
    db.commit()
    return rv

def query_post(p_id):
    db = get_db()
    sql = 'SELECT * FROM Posts WHERE id=?;'
    cur = db.execute(sql, [p_id])
    rv = cur.fetchone()
    cur.close()
    db.commit()
    return rv

def query_posts(u_id):
    db = get_db()
    sql = 'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) OR p.u_id=? ORDER BY p.creation_time DESC;'
    cur = db.execute(sql, (u_id, u_id, u_id))
    rv = cur.fetchall()
    cur.close()
    db.commit()
    return rv

def query_comments(p_id):
    db = get_db()
    sql = 'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id=? ORDER BY c.creation_time DESC;'
    cur = db.execute(sql, [p_id])
    rv = cur.fetchall()
    cur.close()
    db.commit()
    return rv


def submit_user(username, first_name, last_name, password):
    db = get_db()
    sql = 'INSERT INTO Users (username, first_name, last_name, password) VALUES(?, ?, ?, ?);'
    cur = db.execute(sql, (username, first_name,last_name,password))
    rv = cur.fetchone()
    cur.close()
    db.commit()
    return rv

def submit_friend(user, friend):
    db = get_db()
    sql = 'INSERT INTO Friends (u_id, f_id) VALUES(?, ?);'
    cur = db.execute(sql, (user, friend))
    cur.close()
    db.commit()

def submit_post(u_id, content, image, creation_time):
    db = get_db()
    sql = 'INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?);'
    cur = db.execute(sql, (u_id, content,image,creation_time))
    cur.close()
    db.commit()

def submit_comment(p_id, u_id, comment, creation_time):
    db = get_db()
    sql = 'INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?);'
    cur = db.execute(sql, (p_id, u_id, comment,creation_time))
    cur.close()
    db.commit()

def update_profile(education, employment, music, movie, nationality, birthday, username):
    db = get_db()
    sql = 'UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=? ;'
    cur = db.execute(sql, (education, employment, music, movie, nationality, birthday, username))
    cur.close()
    db.commit()
