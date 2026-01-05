---
lang: ko
---

# PandocGUI 도움말

## 개요

PandocGUI는 Pandoc을 사용하여 Markdown 파일을 HTML 및 기타 형식으로 변환하는 간단한 GUI 도구입니다. Lua 필터를 사용하여 Mermaid 및 PlantUML과 같은 다이어그램을 자동으로 생성할 수 있습니다.

## 주요 기능

- **파일/폴더 변환**: 단일 파일 변환 또는 폴더의 여러 파일 일괄 처리
- **Lua 필터**: diagram.lua와 같은 필터를 적용하여 다이어그램 생성
- **CSS 스타일**: 사용자 정의 스타일시트 적용(내장/외부 링크)
- **프로필 관리**: 자주 사용하는 설정 저장 및 로드
- **제외 패턴**: 폴더 변환 중 특정 파일 건너뛰기
- **로그 표시**: 변환 진행 상황 및 오류 모니터링

## 기본 사용법

### 1. 입력 선택

**파일을 변환하려면:**

1. "파일 선택" 버튼 클릭
2. 변환할 Markdown 파일(.md) 선택

**폴더를 일괄 변환하려면:**

1. "폴더 선택" 버튼 클릭
2. Markdown 파일이 포함된 폴더 선택
3. 하위 폴더의 파일도 자동으로 처리됩니다

### 2. 출력 대상 설정

1. "출력 대상 선택" 버튼 클릭
2. 변환된 파일을 저장할 폴더 선택

### 3. 필터 구성

**사전 설정 필터 추가:**

1. "사전 설정 필터" 드롭다운에서 선택
2. "추가" 버튼 클릭

**사용자 필터 추가:**

1. "찾아보기" 버튼을 클릭하여 `.lua` 파일 선택
2. "추가" 버튼 클릭

**필터 순서 변경:**

- 필터 목록에서 항목 선택
- "↑" "↓" 버튼을 사용하여 순서 조정

**필터 제거:**

- 필터 목록에서 항목 선택
- "삭제" 버튼 클릭

### 4. CSS 스타일 구성

1. "CSS 스타일시트 설정" 버튼 클릭
2. CSS 파일 선택
3. 적용 방법 선택:
   - **내장**: CSS를 HTML 파일 내에 내장
   - **외부 링크**: 별도 파일로 출력하고 HTML에서 링크

### 5. 제외 패턴 구성(폴더 변환용)

폴더 변환 중 특정 파일을 건너뛰려면:

1. "제외 패턴 관리" 버튼 클릭
2. 제외 패턴 창이 열림
3. 패턴 입력(한 줄에 하나씩)
4. "확인" 클릭

**패턴 예시:**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. 변환 실행

1. 모든 설정 확인
2. "변환 실행" 버튼 클릭
3. 로그 창에서 진행 상황 확인

## 프로필 기능

자주 사용하는 설정 조합을 프로필로 저장할 수 있습니다.

### 프로필 생성

1. "추가" 버튼 클릭
2. 새 프로필 이름 입력
3. "확인" 클릭
4. 기본 프로필 설정이 복사됩니다

### 프로필 선택

1. 프로필 드롭다운에서 선택
2. 설정이 자동으로 로드됩니다

### 프로필 저장

1. 설정 조정
2. 드롭다운에서 대상 프로필 선택
3. "저장" 버튼 클릭
4. 현재 설정이 프로필에 저장됩니다

### 프로필 삭제

1. 드롭다운에서 삭제할 프로필 선택
2. "삭제" 버튼 클릭
3. 확인 대화 상자에서 "예" 클릭

**참고:** 기본 프로필은 삭제할 수 없습니다.

### 프로필 업데이트

1. "로드" 버튼 클릭
2. 프로필이 최신 설정 항목으로 업데이트됩니다 (하위 호환성)

저장된 프로필은 `profiles/` 폴더에 JSON 형식으로 저장됩니다.

## PlantUML / Java 구성

PlantUML 다이어그램을 사용할 때 두 가지 실행 방법이 있습니다.

### PlantUML 실행 방법 선택

**JAR 방식 (로컬 실행):**

1. "실행 방법"에서 "JAR파일" 선택
2. Java 실행 파일 경로 지정
3. PlantUML JAR 파일 경로 지정

**서버 방식 (온라인 실행):**

1. "실행 방법"에서 "서버" 선택
2. PlantUML 서버 URL 지정 (기본값: http://www.plantuml.com/plantuml)
3. Java/JAR 파일 불필요

### PlantUML JAR 방식 구성

경로는 다음 우선 순위로 검색됩니다:

#### PlantUML JAR 파일

1. GUI 설정 경로
2. 문서의 YAML 메타데이터 `plantuml_jar`
3. 환경 변수 `PLANTUML_JAR`
4. 기본값 `plantuml.jar`

#### Java 실행 파일

1. GUI 설정 경로
2. 문서의 YAML 메타데이터 `java_path`
3. 환경 변수 `JAVA_PATH`
4. 환경 변수 `JAVA_HOME\bin\java`
5. PATH에서 `java`

### 환경 변수 구성 예시

**PowerShell:**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**명령 프롬프트:**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### YAML 메타데이터 지정

Markdown 파일 시작 부분에 추가:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

**서버 방식 사용 시:**

```yaml
---
plantuml_server: true
plantuml_server_url: http://www.plantuml.com/plantuml
---
```

## 자동 업데이트 기능

애플리케이션을 업데이트하면 다음 파일이 자동으로 업데이트됩니다:

### 필터 파일

- `filters/` 폴더의 내장 필터 (diaglam.lua, md2html.lua, wikilink.lua)
- 업데이트 시 최신 버전으로 자동 업데이트
- 사용자 추가 필터는 보호됨

### 프로필 설정

- 새 버전에서 추가된 새 설정이 자동으로 보완됨
- 기존 설정은 보존됨
- 기본값은 `profiles/default.json`에서 가져옴

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### YAML 메타데이터에서 지정

Markdown 파일 시작 부분에 추가:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

## 문제 해결

### Pandoc을 찾을 수 없음

**증상:**

- 시작 시 경고 대화 상자 표시
- 변환을 실행할 수 없음

**해결 방법:**

1. Pandoc 설치: https://pandoc.org/installing.html
2. 설치 후 PATH에 추가되었는지 확인
3. 명령 프롬프트에서 `pandoc --version`을 실행하여 확인

### 변환 실패

**확인 사항:**

- Pandoc이 설치되어 있고 PATH에 추가되어 있습니까?
- 입력 파일이 올바른 Markdown 형식입니까?
- 출력 폴더에 쓰기 권한이 있습니까?

**로그 확인:**

- GUI 로그 창에서 오류 메시지 확인
- `pandoc.log` 파일에서 세부 정보 확인

### 다이어그램이 생성되지 않음

**Mermaid 다이어그램의 경우:**

- `mmdc`(mermaid-cli)가 설치되어 있는지 확인
- 명령 프롬프트에서 `mmdc --version`을 실행하여 확인

**PlantUML 다이어그램의 경우:**

**JAR 방식:**
- `plantuml.jar`이 존재하는지 확인
- Java가 설치되어 있는지 확인
- GUI 설정, 환경 변수 또는 YAML 메타데이터에서 경로 지정

**서버 방식:**
- 인터넷 연결 확인
- 서버 URL이 올바른지 확인 (기본값: http://www.plantuml.com/plantuml)
- 방화벽 설정 확인

### 필터가 적용되지 않음

**확인 사항:**

- 필터가 올바르게 추가되었습니까? (필터 목록 확인)
- Lua 파일이 올바른 경로에 존재합니까?
- 필터 순서가 적절합니까? (diagram.lua는 특정 순서가 필요할 수 있음)

### 제외 패턴이 작동하지 않음

**확인 사항:**

- 패턴 구문이 올바릅니까? (와일드카드 `*` 사용)
- 패턴이 파일 이름 또는 폴더 이름과 일치합니까?
- 제외 패턴 창에서 "확인"을 클릭하여 저장했습니까?

## 자주 묻는 질문

### Q: 어떤 파일 형식으로 변환할 수 있습니까?

A: Pandoc이 지원하는 모든 형식으로 변환할 수 있습니다. 주요 형식은 다음과 같습니다:

- HTML
- PDF(LaTeX 필요)
- DOCX(Word)
- EPUB
- 기타 다수

출력 형식은 Pandoc 옵션으로 지정할 수 있습니다(향후 버전에서 지원 예정).

### Q: 여러 CSS 파일을 사용할 수 있습니까?

A: 현재 버전은 하나의 CSS 파일만 지원합니다. 여러 스타일이 필요한 경우 CSS 파일을 결합하세요.

### Q: 폴더 변환 시 파일 구조가 유지됩니까?

A: 예, 입력 폴더의 하위 폴더 구조는 출력 대상에서 유지됩니다.

### Q: 변환을 취소할 수 있습니까?

A: 창을 닫아 변환 프로세스를 안전하게 종료할 수 있습니다. 처리 중인 파일은 완료되지만 나머지 파일은 취소됩니다.

## 로그 파일

변환 세부 정보는 다음 로그 파일에 기록됩니다:

- **위치**: `pandoc.log`(실행 파일과 같은 폴더)
- **내용**: Pandoc 출력, 오류 메시지, 필터 실행 결과

문제가 발생하면 이 로그 파일을 확인하세요.

## 부록: 필터 정보

### 사전 설정 필터

`filters/` 폴더에 배치된 Lua 필터는 자동으로 감지됩니다.

**diagram.lua:**

- Mermaid, PlantUML 등의 코드 블록을 다이어그램으로 변환

**md2html.lua:**

- Markdown 내에서 추가 처리 수행

**wikilink.lua:**

- Wiki 형식 링크 변환

### 사용자 정의 필터 추가

1. 임의의 위치에 `.lua` 파일 생성
2. "사용자 필터" 섹션의 "찾아보기" 버튼 클릭
3. 생성한 Lua 파일 선택
4. "추가" 버튼 클릭

## 지원 정보

문제가 해결되지 않으면 다음 정보와 함께 보고하세요:

- 사용 중인 PandocGUI 버전
- Pandoc 버전(`pandoc --version`)
- 오류 메시지(로그 창 또는 `pandoc.log`에서)
- 수행한 단계
- 샘플 입력 파일(가능한 경우)

---

**PandocGUI** - Pandoc용 간단한 GUI 프론트엔드
