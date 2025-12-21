# Pandoc GUI

[English](README.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [Français](README.fr.md) | [Italiano](README.it.md)

Lua 필터를 사용하여 다이어그램(Mermaid, PlantUML 등)을 생성하는 간단한 Pandoc GUI 프론트엔드입니다. Windows용으로 설계되었습니다.

## 기능

- 파일/폴더 선택 및 출력 대상 설정
- `filters/` 디렉토리의 Lua 필터 적용(사전 설정 + 사용자 추가)
- CSS 스타일 설정(`stylesheets/` 디렉토리), 임베드 또는 외부 링크 선택
- 프로필 저장/로드(`profiles/*.json`)
- 로그 출력(GUI 및 `pandoc.log`)
- 백그라운드에서 Pandoc 실행, 앱 종료 시 하위 프로세스 안전하게 종료

## 요구 사항

- Python 3.8+
- Pandoc(PATH에 추가)
- Mermaid용: `mmdc`(mermaid-cli)
- PlantUML용: `plantuml.jar` 및 Java(jdk/jre)
- (선택 사항) 필요한 Lua 필터(`filters/*.lua`)

## 실행 방법

1. 필요한 도구 설치(Pandoc, Node/mmdc, Java 등)
2. 저장소 루트에서 실행:

    ```powershell
    python main_window.py
    ```

## PlantUML / Java 경로 지정

다음 방법을 사용하여 PlantUML JAR 및 Java 실행 파일을 지정합니다(우선 순위 순서):

- PlantUML JAR: 문서 YAML 메타데이터 `plantuml_jar` → 환경 변수 `PLANTUML_JAR` → `plantuml.jar`
- Java 실행 파일: 문서 YAML 메타데이터 `java_path` → 환경 변수 `JAVA_PATH` → `JAVA_HOME\bin\java` → `java`(PATH)

Windows 환경 변수 예제(명령 프롬프트):

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell:

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

문서의 YAML 지정 예제:

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## 사용 방법(GUI)

1. "파일 선택" 또는 "폴더 선택"으로 입력 선택
2. "출력 대상 선택"으로 출력 디렉토리 선택
3. 사전 설정/사용자 필터 추가(위/아래 버튼으로 순서 조정)
4. (선택 사항) 폴더 변환 중 특정 파일을 건너뛰도록 제외 패턴 구성
5. "변환 실행" 클릭

### 제외 패턴 설정

폴더를 일괄 변환할 때 특정 파일이나 폴더를 제외할 수 있습니다:

- "제외 패턴 관리"를 클릭하여 설정 열기
- 와일드카드 패턴 지원(예: `*.tmp`, `__pycache__`, `.git`)
- 여러 패턴 지원(한 줄에 하나씩)

패턴 매칭 예제:

- `*.tmp` - 모든 .tmp 파일 제외
- `__pycache__` - __pycache__ 폴더 및 내용 제외
- `.git` - .git 폴더 제외
- `test_*` - test_로 시작하는 파일 제외
- `*_backup` - _backup으로 끝나는 파일 제외

## 로그 및 프로필

- GUI에 로그가 표시되고 시스템이 `pandoc.log`에 세부 정보를 기록합니다
- 시스템은 프로필을 `profiles/` 디렉토리에 JSON으로 저장합니다

## 배포 패키지 생성

### PyInstaller로 폴더 배포 생성

1. PyInstaller 설치:

    ```powershell
    pip install pyinstaller
    ```

2. 실행 파일 생성:

    __참고__: `PandocGUI.spec`는 저장소에 포함되어 있으며 `filters/` 및 `locales/`를 `_internal/` 외부에 배치하도록 빌드 후 처리가 구성되어 있습니다.

    ```powershell
    python -m PyInstaller PandocGUI.spec
    ```

    `.spec` 파일을 재생성해야 하는 경우에만(일반적으로 필요하지 않음):

    ```powershell
    pyinstaller --noconsole --onedir --name "PandocGUI" `
      --add-data "locales;locales" `
      --add-data "filters;filters" `
      --add-data "stylesheets;stylesheets" `
      main_window.py
    ```

    __중요__: 위 명령으로 생성된 `.spec` 파일에 빌드 후 처리를 수동으로 추가해야 합니다.

3. 빌드 출력은 `dist/PandocGUI/`에 있습니다:

    ```text
    dist/PandocGUI/
    ├── PandocGUI.exe        # 실행 파일
    ├── filters/             # Lua 필터
    ├── locales/             # 번역 파일
    ├── stylesheets/         # CSS 스타일시트
    ├── help/                # 도움말 파일(HTML)
    ├── profiles/            # 프로필(런타임에 생성)
    └── _internal/           # Python 종속성
    ```

    `.spec` 파일의 빌드 후 처리는 `filters/`, `locales/`, `stylesheets/`를 `_internal/` 외부에 배치합니다

### MSIX Packaging Tool로 Windows 설치 프로그램 생성

1. MSIX Packaging Tool 설치:

   - Microsoft Store에서 "MSIX Packaging Tool" 설치

2. MSIX Packaging Tool을 시작하고 "Application package" 선택

3. "Create package on this computer" 선택

4. 패키지 정보 입력:

    - Package name: `PandocGUI`
    - Publisher: `CN=YourName`(인증서에 따라 변경)
    - Version: `1.0.0.0`

5. 설치 프로그램 선택:

    - "Browse"를 클릭하고 `dist/PandocGUI/PandocGUI.exe` 선택
    - Installation location: `C:\Program Files\PandocGUI`

6. 설치 실행 및 캡처:

   - 앱을 시작하고 작동 확인
   - 필요한 모든 파일이 포함되어 있는지 확인
   - "Done" 클릭

7. 패키지 저장:

    - .msix 파일로 저장

8. 서명(선택 사항):

    - 테스트 인증서 생성 또는 기존 인증서 사용

    ```powershell
    # 테스트 인증서 생성
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # MSIX 파일 서명
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. 설치 프로그램 배포:

   - .msix 파일 배포
   - 사용자는 앱을 설치하기 전에 인증서를 설치합니다

### 참고 사항

- `filters/` 및 `locales/`와 같은 리소스 파일이 올바르게 포함되어 있는지 확인
- Pandoc, mmdc, Java와 같은 외부 도구는 별도로 설치해야 합니다
- MSIX 패키지는 서명이 필요합니다(개발 중에는 테스트 인증서를 사용할 수 있음)

## 테스트

단위 테스트를 제공합니다. 다음 명령으로 실행하세요:

### 모든 테스트 실행

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### 개별 테스트 파일 실행

```powershell
python -m unittest test_<name>.py
```

예제:

```powershell
python -m unittest test_main_window.py
```

### 상세 테스트 출력

```powershell
python -m unittest discover -v
```

테스트 파일:

- `test_main_window.py` - 메인 윈도우 및 프로필 관리 기능
- `test_css_window.py` - CSS 설정 기능
- `test_filter_window.py` - 필터 관리 기능
- `test_log_window.py` - 로그 표시 기능

## 문제 해결

- 시스템이 PlantUML을 찾을 수 없거나 Java를 실행할 수 없는 경우 stderr에 메시지가 나타납니다. 환경 변수 또는 YAML 메타데이터를 사용하여 경로를 지정하세요.
- 시스템은 GUI 로그 및 `pandoc.log`에 Pandoc 오류를 표시합니다.

## 개발 참고 사항

- Lua 필터를 `filters/` 디렉토리에 배치합니다(예: `filters/diagram.lua`).
- CSS 파일을 `stylesheets/` 디렉토리에 배치합니다. GUI에서 선택하여 임베디드 또는 외부 링크로 적용할 수 있습니다.
- 시스템은 백그라운드 스레드에서 변환을 수행하고 앱 종료 시 하위 프로세스를 종료/중지합니다.
