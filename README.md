mac-launchd-autocrawl

**더 이상 이 레포는 개발 및 유지보수를 진행하지 않습니다.**  
개발을 중단한 이유와 이후 계획은 아래와 같습니다:

1. 크롤링에 파이썬을 사용했으나, DOM 분석 시간을 줄이기 위해 LLM(대형 언어 모델) 활용을 고민하게 됨
2. LLM에게 특정 페이지의 텍스트만 추출하여 프롬프트로 전달하는 과정에서,
   - HTML 태그 제거는 파이썬뿐 아니라 Node.js로도 가능
   - Node.js 환경에서도 LLM 프롬프팅이 손쉽게 가능
3. 심화 크롤링을 구현할 필요가 없어져, 사실상 파이썬이 하는 일은 HTML 태그 제거에 국한됨
4. ETL(크롤링, 데이터 정제, DB 적재) 자체는 여기서 충분히 구현했으나, 향후 웹 서비스 백엔드 작업을 위해서는 Django 등 추가 학습이 필요
5. 그러나 이전에 사용해봤던 NestJS로 웹 서비스를 구축하는 편이 더 낫다고 판단
6. 따라서, 현재 레포에서는 작업을 중단하고, NestJS 모노레포를 통해 크론/ETL 기능을 진행할 예정

해당 이유로 본 프로젝트는 더 이상 업데이트되지 않으며, 추후 추가 기능 구현이 필요하다면  
[swimming-schedule-nest](https://github.com/jeongkichang/swimming-schedule-nest) 프로젝트에서 계속 개발할 예정입니다.

--------------------------------------------------------------------------------

이 저장소는 Mac 환경에서 Launchd를 활용하여 파이썬 크롤러를 자동으로 실행시키는 예시를 제공하기 위해 만들어졌습니다.
주기적으로 크롤링을 수행할 필요가 없거나, 별도의 서버를 구축할 필요가 없는 경우에 유용합니다.

--------------------------------------------------------------------------------
1. 개요

 - 목적
   * Mac 부팅 시(또는 로그인 시) 한 번만 파이썬 스크립트를 실행하여 크롤링 작업을 수행하도록 설정합니다.
   * 별도의 서버를 두고 크론(cron)을 돌릴 필요가 없으므로, 가볍게 개인 맥에서 크롤링을 자동화할 수 있습니다.

 - 방식
   * User 단위 LaunchAgent 방식을 사용합니다.
   * /Library/LaunchDaemons(시스템 전역) 대신 ~/Library/LaunchAgents 디렉터리에 .plist 파일을 배치합니다.
   * Mac 부팅 후에 자동으로 한 번만 파이썬 스크립트를 실행하도록 설정합니다.

--------------------------------------------------------------------------------
2. 사용 방법

(1) plist 파일 준비
  - 예시 파일: com.username.bootcrawl.plist
  - 이 파일은 User 계정에서 동작하도록 작성되었습니다.
  - (예시 이름) com.username.bootcrawl.plist를 ~/Library/LaunchAgents 경로에 복사 또는 생성합니다.
  - 아래와 같이 ProgramArguments에 실제 파이썬 스크립트 경로를 지정합니다:
```
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/env</string>
      <string>python3</string>
      <string>/Users/username/my_crawler/run.py</string>
    </array>
```

/Users/username/my_crawler/run.py 위치에 실제로 실행할 파이썬 크롤러 스크립트를 배치하세요.

(2) 파이썬 스크립트 준비

예: /Users/username/my_crawler/run.py
크롤링 동작을 위한 코드를 직접 작성합니다.
실행 여부 확인을 위해 로그 파일 작성이나 콘솔 출력이 필요하다면, 코드에 추가해 주세요.

(4) Launchd 로드
  - plist 파일을 load해서 Launch Agent로 등록합니다:
    launchctl load -w ~/Library/LaunchAgents/com.username.bootcrawl.plist
  - -w 옵션은 "영구적으로(override 설정) 등록"을 의미합니다.
  - Mac을 재부팅하면, 부팅 시점에 main.py 스크립트가 한 번 실행됩니다.

(5) 수정 후 재로드
  - plist 파일을 수정한 뒤에는 다음과 같이 먼저 unload 후 다시 load해야 합니다:

```
    launchctl unload ~/Library/LaunchAgents/com.username.bootcrawl.plist
    launchctl load -w ~/Library/LaunchAgents/com.username.bootcrawl.plist
```

(6) 실행 확인
  - 재부팅 후(또는 사용자 로그인 시) run.py가 자동으로 실행되는지 확인합니다.
  - 로그 파일 등을 통해 실행 결과를 확인하실 수 있습니다.

--------------------------------------------------------------------------------
3. 참고 사항

 - 반복 실행
   * 현재 설정은 "부팅 시 한 번만" 실행됩니다.
   * 주기적으로 실행하고 싶다면, plist 내 StartInterval 또는 StartCalendarInterval 등을 사용할 수 있습니다.

 - 경로 주의
   * plist 내부의 ProgramArguments에는 반드시 절대 경로를 사용해야 합니다.
   * 파이썬 스크립트(crawl.py)에 실행 권한을 주거나(chmod +x), Shebang(#!/usr/bin/env python3)을 명시해 두면 편리합니다.

 - cron vs launchd
   * macOS에서는 launchd 방식을 공식적으로 권장합니다.
   * cron에서 @reboot 옵션을 사용할 수도 있지만, macOS 환경에서는 launchd가 더 안정적이고 선호되는 방법입니다.

--------------------------------------------------------------------------------
4. 라이선스

 - 필요에 따라 자유롭게 참고하거나 수정해서 사용하셔도 됩니다.
 - 자세한 내용은 LICENSE 파일을 참고하세요.

--------------------------------------------------------------------------------
5. 기여 방법

 - 이 저장소는 학습 및 예시 제공을 위해 만들어졌습니다.
 - 제안사항이나 문제점이 있다면 Issues나 Pull Request를 통해 기여해 주세요.

--------------------------------------------------------------------------------
6. 문의

 - 작성자: @jeongkichang (https://github.com/jeongkichang)
 - 궁금한 점이나 도움이 필요하시면 Issues에 남겨주시면 됩니다.
