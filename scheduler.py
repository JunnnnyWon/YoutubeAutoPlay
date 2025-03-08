from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import queue
import json
import os

class YouTubeScheduler:
    def __init__(self, browser_controller):
        self.scheduler = BackgroundScheduler()
        self.browser_controller = browser_controller
        self.active_jobs = {}
        self.logger = logging.getLogger("YouTubeScheduler")
        self.notification_queue = queue.Queue()  # 알림을 저장할 큐
        self.jobs_file = "youtube_jobs.json"  # 작업 저장 파일 경로
        
        # 저장된 작업 로드
        self.load_jobs()
        
        self.scheduler.start()

    def add_job(self, job_id, start_time, end_time, youtube_url):
        """새 작업 추가"""
        try:
            # 시작 작업 추가
            start_hour, start_minute = map(int, start_time.split(':'))
            start_trigger = CronTrigger(hour=start_hour, minute=start_minute)
            
            self.scheduler.add_job(
                self._start_youtube,
                start_trigger,
                args=[job_id, youtube_url],
                id=f"{job_id}_start"
            )
            
            # 종료 작업 추가
            end_hour, end_minute = map(int, end_time.split(':'))
            end_trigger = CronTrigger(hour=end_hour, minute=end_minute)
            
            self.scheduler.add_job(
                self._end_youtube,
                end_trigger,
                args=[job_id],
                id=f"{job_id}_end"
            )
            
            self.active_jobs[job_id] = {
                "start_time": start_time,
                "end_time": end_time,
                "youtube_url": youtube_url,
                "status": "대기중"
            }
            
            # 작업 저장
            self.save_jobs()
            
            return True, f"작업 {job_id}가 성공적으로 추가되었습니다."
        except Exception as e:
            error_msg = f"작업 추가 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def remove_job(self, job_id):
        """작업 제거"""
        try:
            if job_id in self.active_jobs:
                try:
                    self.scheduler.remove_job(f"{job_id}_start")
                except:
                    pass
                
                try:
                    self.scheduler.remove_job(f"{job_id}_end")
                except:
                    pass
                
                del self.active_jobs[job_id]
                
                # 작업 저장
                self.save_jobs()
                
                return True, f"작업 {job_id}가 성공적으로 제거되었습니다."
            else:
                return False, f"작업 {job_id}를 찾을 수 없습니다."
        except Exception as e:
            error_msg = f"작업 제거 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def get_all_jobs(self):
        """모든 작업 가져오기"""
        return self.active_jobs
    
    def get_notifications(self):
        """큐에서 모든 알림을 가져옴"""
        notifications = []
        while not self.notification_queue.empty():
            notifications.append(self.notification_queue.get())
        return notifications
    
    def save_jobs(self):
        """작업을 파일에 저장"""
        try:
            with open(self.jobs_file, 'w') as f:
                json.dump(self.active_jobs, f)
            self.logger.info(f"작업이 {self.jobs_file}에 저장되었습니다.")
        except Exception as e:
            self.logger.error(f"작업 저장 중 오류 발생: {str(e)}")
    
    def load_jobs(self):
        """파일에서 작업 로드"""
        try:
            if os.path.exists(self.jobs_file):
                with open(self.jobs_file, 'r') as f:
                    self.active_jobs = json.load(f)
                    
                # 스케줄러에 작업 등록
                for job_id, job_info in self.active_jobs.items():
                    try:
                        # 시작 작업 추가
                        start_hour, start_minute = map(int, job_info["start_time"].split(':'))
                        start_trigger = CronTrigger(hour=start_hour, minute=start_minute)
                        
                        self.scheduler.add_job(
                            self._start_youtube,
                            start_trigger,
                            args=[job_id, job_info["youtube_url"]],
                            id=f"{job_id}_start"
                        )
                        
                        # 종료 작업 추가
                        end_hour, end_minute = map(int, job_info["end_time"].split(':'))
                        end_trigger = CronTrigger(hour=end_hour, minute=end_minute)
                        
                        self.scheduler.add_job(
                            self._end_youtube,
                            end_trigger,
                            args=[job_id],
                            id=f"{job_id}_end"
                        )
                        
                        # 상태 업데이트
                        job_info["status"] = "대기중"
                    except Exception as e:
                        self.logger.error(f"작업 {job_id} 로드 중 오류: {str(e)}")
                
                self.logger.info(f"{len(self.active_jobs)}개의 작업이 {self.jobs_file}에서 로드되었습니다.")
            else:
                self.active_jobs = {}
                self.logger.info(f"작업 파일 {self.jobs_file}가 존재하지 않습니다. 빈 작업 목록으로 시작합니다.")
        except Exception as e:
            self.active_jobs = {}
            self.logger.error(f"작업 로드 중 오류 발생: {str(e)}")

    def _start_youtube(self, job_id, youtube_url):
        """유튜브 시작 작업 실행"""
        try:
            success, message = self.browser_controller.start_browser(youtube_url)
            if success:
                status = "실행중"
            else:
                status = "오류"
            
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = status
                # 상태 변경 후 저장
                self.save_jobs()
            
            # 큐에 알림 추가
            notification = {
                "type": "start" if success else "error",
                "job_id": job_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": success,
                "message": message
            }
            self.notification_queue.put(notification)
                
            return success, message
        except Exception as e:
            error_msg = f"유튜브 시작 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = "오류"
                # 상태 변경 후 저장
                self.save_jobs()
                
            # 큐에 오류 알림 추가
            notification = {
                "type": "error",
                "job_id": job_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": error_msg
            }
            self.notification_queue.put(notification)
                
            return False, error_msg

    def _end_youtube(self, job_id):
        """유튜브 종료 작업 실행"""
        try:
            success, message = self.browser_controller.close_browser()
            if success:
                status = "완료"
            else:
                status = "오류"
            
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = status
                # 상태 변경 후 저장
                self.save_jobs()
            
            # 큐에 알림 추가
            notification = {
                "type": "end" if success else "error",
                "job_id": job_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": success,
                "message": message
            }
            self.notification_queue.put(notification)
                
            return success, message
        except Exception as e:
            error_msg = f"유튜브 종료 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = "오류"
                # 상태 변경 후 저장
                self.save_jobs()
                
            # 큐에 오류 알림 추가
            notification = {
                "type": "error",
                "job_id": job_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": error_msg
            }
            self.notification_queue.put(notification)
                
            return False, error_msg

    def shutdown(self):
        """스케줄러 종료"""
        if self.scheduler.running:
            self.scheduler.shutdown()
