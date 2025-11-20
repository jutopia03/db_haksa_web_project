# db_haksa_web_project
데이터베이스 구축 팀프로젝트 학사관리 웹 만들기
## 🔔 Project Rules
- main 브랜치는 배포용, 직접 push 금지
- 기능은 각자 feature 브랜치에서 개발 후 PR
- DB 스키마 변경은 팀원 전체 합의 필수
- push 전 항상 pull
- 환경 변수는 .env 관리, Git에 올리지 않기
- 역할별 파트 존중하며 남의 기능을 임의로 수정 금지
- 이슈 발생 시 즉시 공유

### 1. DB 생성 (.sql 파일 실행)
1. 이 레포지토리를 clone 또는 pull:
   - `git clone ...`
2. MySQL Workbench 실행
3. `File > Open SQL Script...` 선택
4. `db/schema_and_data.sql` 파일 열기
5. 상단 번개(⚡) 버튼으로 스크립트 전체 실행

### 2. 스키마 확인
- SCHEMAS에서 `haksadb`가 보이는지 확인
- `student`, `professor`, `course`, `enrollment`, `account` 등 테이블이 생성되어 있어야 함

### 3. 웹 앱 DB 설정
- 웹 프로젝트 설정 파일에서 DB 정보를 아래처럼 맞춘다 (예시):

  ```env
  DB_HOST=localhost
  DB_USER=본인_유저명
  DB_PASSWORD=본인_비밀번호
  DB_NAME=haksadb
