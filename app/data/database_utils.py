from sqlalchemy.orm import session, sessionmaker
from contextlib import contextmanager
from app.data.models import VdcaBase

def models_to_json(model_list: list):
    # TODO: this is a monstrosity.  The sooner we can not do this, the better.
    output = []
    for m in model_list:
        row = {}

        for field in m.__table__.c:
            output_key = str(field).replace(m.__tablename__ + ".", "")
            row[output_key] = getattr(m, output_key, None)

        output.append(row)
    return output

class VdcaDatabase():

    def __init__(self, engine=None):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    @contextmanager
    def yield_session(self) -> session:
        the_session = self.Session()
        try:
            yield the_session
            the_session.flush()
            the_session.commit()
        except Exception as e:
            the_session.rollback()
            raise e
        finally:
            the_session.close()

    def query_unique_record(self, tabletype: VdcaBase, player_id, team_id, season, finals_flag, grade_id):
        with self.yield_session() as s:
            result = s.query(tabletype).filter_by(player_id=player_id, team_id=team_id, season=season, finals_flag=finals_flag, grade_id=grade_id).all()
        return result

    def query_stats_by_season_finals_grade(self, tabletype: VdcaBase, season, finals_flag, grade_id):
        with self.yield_session() as s:
            result = s.query(tabletype).filter_by(season=season, finals_flag=finals_flag, grade_id=grade_id).all()
        return result