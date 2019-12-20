from sqlalchemy.orm import session, sessionmaker
from contextlib import contextmanager
from data.models import BattingStats, VdcaBase

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

    def query_unique_record(self, tabletype: VdcaBase, player_id, team_id, season, finals_flag):
        with self.yield_session() as s:
            result = s.query(tabletype).filter_by(player_id=player_id, team_id=team_id, season=season, finals_flag=finals_flag).all()
        return result
