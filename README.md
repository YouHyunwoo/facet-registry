# Facet 레지스트리 템플릿

공개 저장소 `YouHyunwoo/facet-registry`의 내용입니다. 이 폴더를 그 저장소의 루트로 올립니다. 결정 배경은 ADR 0088에 있습니다.

## 저장소 준비

1. 이 폴더 내용을 `main`에 올리고 `submission` 라벨을 만듭니다.
2. Settings → Actions → General에서 **Read and write permissions**와 **Allow GitHub Actions to create and approve pull requests**를 켭니다.
3. `main` 보호 규칙에서 pull request 리뷰를 요구하면 봇의 스킨 직접 푸시가 막히므로, 봇을 예외로 두거나 일반 푸시 제한만 설정합니다.

## 흐름

GitHub 로그인 사용자가 제출 양식에 zip을 첨부하면 `tools/submission.py`가 검증합니다. 스킨은 바로 `index.json`에 올라가고, 플러그인은 pull request로 대기하며 병합이 승인입니다. 같은 ID는 처음 올린 작성자만 갱신할 수 있습니다.

검사: `python registry/tools/test_submission.py`
