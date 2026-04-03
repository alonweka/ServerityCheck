# SeverityCheck

**Purpose:** Single reference for WEKAPP bug **Priority** (Critical / Major / Minor / Blocker) decisions, Notion page updates, and JIRA audit results.

**Canonical policy:** Notion — *Bug Severity Definition – Weka.io*. This file contains **proposed Notion additions** (copy-paste blocks), **severity criteria summary**, **reconciled guidance** where audits disagree, and **CSV-based ticket reviews**. The live Notion page remains authoritative for the full formal definition (all sections); paste proposed deltas from Section 4 there.

**Last consolidated:** 2026-04-03.

---

## Table of contents

1. [How to use this document](#how-to-use-this-document)
2. [Severity framework (quick reference)](#severity-framework-quick-reference)
3. [Reconciled guidance: audits vs. Notion misclassification examples](#reconciled-guidance-audits-vs-notion-misclassification-examples)
4. [Notion page — proposed additions and examples (full text)](#notion-page--proposed-additions-and-examples-full-text)
5. [Regression from previous release — severity review](#regression-from-previous-release--severity-review)
6. [Regression unhandled issues — severity review](#regression-unhandled-issues--severity-review)

---

## How to use this document

- **Change Priority in JIRA** at [https://wekaio.atlassian.net](https://wekaio.atlassian.net); use rationale columns as internal notes or comments when needed.
- **Update Notion** using Section 4 (full text from the former `Notion_Bug_Severity_Updates_CopyPaste.md` workflow).
- **Conflicts:** If the [Regression unhandled](#regression-unhandled-issues--severity-review) table marks a ticket Critical while Section 4 *Misclassification* says Major, use [Reconciled guidance](#reconciled-guidance-audits-vs-notion-misclassification-examples) unless new root-cause evidence changes the decision.

---

## Severity framework (quick reference)

Synthesized from the formal Bug Severity Definition (Notion §5.2) as referenced in team audits. **Severity follows product customer impact**, not CI convenience.

| Criterion | Critical when |
|-----------|----------------|
| **1 — Crash / ASSERT** | Genuine product crash (SIGSEGV, SIGABRT) or product ASSERT on data/management path under customer-relevant conditions — with nuance: **not every ASSERT or CriticalEvent is automatically Critical** (verify root cause). |
| **2 — Deployment / feature blocked** | Valid upgrade, install, or important feature blocked by a **product** bug (distinguish lab config, test timeout, and post-upgrade **test** assertion). |
| **3 — DUDL / corruption** | Data unavailability, loss, or corruption risk; **metadata (e.g. S3 object tags) treated like data loss** per proposed Notion addition. |
| **4 — Severe availability** | Critical events or hangs that block the storage path, protocol down, driver hang, redundancy loss endangering data — scale by whether the scenario is general vs. test-induced. |

**Typical Major:** Port tests, setup/teardown, DNS/lab, `ExceptionNotRaised`, infra/workflow bugs without customer runtime impact, Infra/Test/Devops components when root cause is not product code.

---

## Reconciled guidance: audits vs. Notion misclassification examples

The [Regression unhandled](#regression-unhandled-issues--severity-review) review includes detailed “why Critical” text written before some tickets were aligned with the Notion *Examples of misclassification* table. **Prefer the following** when setting JIRA Priority unless investigation proves otherwise.

| Ticket | Reconciled severity | Notes |
|--------|---------------------|-------|
| WEKAPP-591290 | **Major** | `UpgradeFailed` / verify rebuild — not automatically Critical; see Notion example. |
| WEKAPP-591313 | **Major** | CriticalEvent CacheFlushHanging — may be test-induced; verify general defect. |
| WEKAPP-569646 | **Major** | ASSERT FailedDisksTable — verify test-induced vs. genuine data-path defect. |
| WEKAPP-568145 | **Major** | `after_upgrade` / buckets_list_statuses — may be test assertion. |
| WEKAPP-586233 | **Major** | Scheduler/validation — consider impact breadth; not all correctness bugs → Critical. |

**Confirmed Critical (examples from manual verification / team agreement):** WEKAPP-581666 (SIGABRT), WEKAPP-587554, WEKAPP-579018, WEKAPP-552659, WEKAPP-591224, WEKAPP-591707 — align with Notion examples and criterion mapping.

---

## Notion page — proposed additions and examples (full text)

*Starts below: complete export of `Notion_Bug_Severity_Updates_CopyPaste.md` (placement map, §1–§8, quick copy blocks).*

---

# Bug Severity Definition – Notion Updates (Copy-Paste Ready)

Use this document to update the Notion "Bug Severity Definition – Weka.io" page. Each section below is ready to copy and paste into Notion.

---

## Where to add each section

| Section | Add after | Action |
|---------|-----------|--------|
| 1. Metadata loss clarification | Section 5.2, criterion 3 (DUDL / Data Corruption) | Insert after "Metadata inconsistencies that can lead to data loss or inaccessibility." |
| 2. Test Run Frequency | Section 7 (Environment) or Section 8 (Reproducibility) | Insert as new section |
| 3. Additional Critical examples | Section 11 (existing examples) | Append to examples |
| 4. Misclassification examples | After Critical examples | Insert as new section |
| 5. Automation Bug / Test guidance | Section 6 (Decision Guide) | Add as subsection or new section |
| 6. Re-evaluation triggers | Section 6 (Decision Guide) | Add at end of Decision Guide |
| 7. V4.4.6 Critical Automation Bugs | After Section 6 or as appendix | Severity review table for JQL audit |
| 8. V5.0 Critical Automation Bugs | After Section 7 or as appendix | Severity review table for JQL audit |

---

## 1. Metadata loss clarification (add to Section 5.2, criterion 3)

**Paste after:** "Metadata inconsistencies that can lead to data loss or inaccessibility."

---

**Metadata loss (including S3 object tags):** Loss or incorrect handling of metadata such as S3 object tags is treated **the same as data loss** for severity classification. Tags affect lifecycle, retention, access control, and compliance; metadata loss can lead to data loss or inaccessibility and is therefore at least **Critical**.

---

## 2. Test Run Frequency and Failure Rate (new section)

**Section title:** ### Test Run Frequency and Failure Rate

---

**Rare tests** (run less than once per week):
- A failure is considered **"interesting"** — it may indicate a regression, flakiness, or environment issue.
- **Many reproductions** across runs increase the likelihood that the issue is Critical and should be prioritized.

**Frequent tests** (run more than once per week):
- If the failure rate is **~20% or higher**, the GL/TL should supply explicit answers: root cause, severity rationale, and residual risk.

**Note:** Run frequency and failure rate influence **priority and investigation focus**. Severity (Critical / Major / Minor) is still driven by **product impact** per the formal definitions above.

---

## 3. Additional Critical Examples (append to existing Section 11)

**Paste after:** The WEKAPP-583009 example block.

---

### Example: Critical – WEKAPP-582005 (S3 connection closed during transfer)

**Ticket:** [WEKAPP-582005](https://wekaio.atlassian.net/browse/WEKAPP-582005)  
**Summary:** Operation Run Workloader Solitary Program failed – Connection was closed before we received a valid response from endpoint URL  
**Component:** Interfaces / S3-FE (S3)  
**Discovered in:** Regression (S3 multipart upload large-object test); branch `s3_remove-symlink-extra`  
**Priority:** Raised from Major to Critical on 2026-01-21 (Nir Shasha).  
**Status:** Done (fixed in v5.1.0, commit 435c4440ee8).

**Why Critical (per this document):**
- **Tier-1 protocol defect (S2):** S3 is a Tier-1 protocol; connection drops during large-object transfer block a primary use case.
- **Data inaccessibility / DUDL risk:** Connection closed during S3 download can prevent customers from retrieving objects.
- **Multiple reproductions** (6 failures) indicate a real product regression.

---

### Example: Critical – WEKAPP-579269 (DestageHanging)

**Ticket:** [WEKAPP-579269](https://wekaio.atlassian.net/browse/WEKAPP-579269)  
**Summary:** DR | destage hanging while RAID nearly full, alloc threshold bug  
**Component:** Filesystem / Data Reduction  
**Discovered in:** Regression (TestDataReductionStressWithFailuresLong)  
**Priority:** Raised from Major to Critical on 2026-01-12 (Maria Shikhman).  
**Status:** Done (fixed in v5.1.0, commit de7f23e2510).

**Why Critical (per this document):**
- **Critical event:** DestageHanging (category=Filesystem, codes=DestageHanging).
- **Severe availability:** Destage hanging blocks core storage path; cache can fill, writes can stall.
- **DUDL risk:** When capacity is tight, destage hang can lead to data unavailability.

---

### Example: Critical – WEKAPP-510638 (RepairedCorruptDataFromDrive)

**Ticket:** [WEKAPP-510638](https://wekaio.atlassian.net/browse/WEKAPP-510638)  
**Summary:** CriticalEventException: RepairedCorruptDataFromDrive – corrupt data read from SSD  
**Component:** Platform / SSD  
**Discovered in:** Automation Bug (V4.4.9)  
**Why Critical:** Explicit data corruption event. Per criterion 3 (DUDL / data corruption), data corruption is always at least Critical.

---

### Example: Critical – WEKAPP-491238 (Driver compile failure)

**Ticket:** [WEKAPP-491238](https://wekaio.atlassian.net/browse/WEKAPP-491238)  
**Summary:** wekafs driver does not compile on centos9 stream  
**Component:** Interfaces / Driver  
**Discovered in:** Automation Bug (V4.4.9)  
**Why Critical:** Blocks installation on a supported platform. Per criterion 2 (feature impact), installation or deployment blocked on supported platform → Critical.

---

### Example: Critical – WEKAPP-525685 (Protection state wrong)

**Ticket:** [WEKAPP-525685](https://wekaio.atlassian.net/browse/WEKAPP-525685)  
**Summary:** AssertionError: numFailures=3, MiB=114688 – protection state incorrect after restart  
**Component:** Clustering / Requested actions  
**Discovered in:** Automation Bug (V4.4.9)  
**Why Critical:** Incorrect drive protection state affects data durability. Per criterion 4 (availability), drive/protection state wrong after restart → Critical.

---

## 4. Examples of Misclassification – Critical vs Major (new section)

**Section title:** ### Examples of Misclassification – Critical vs Major

---

When in doubt, compare new tickets to these patterns:

| Ticket | Issue | Correct Severity | Lesson |
|--------|-------|------------------|--------|
| [WEKAPP-582905](https://wekaio.atlassian.net/browse/WEKAPP-582905) | LTP fcntl34 timeout | **Major** | Fix was "increase timeout"; no product semantics bug. Timeout/test-infra fixes → Major, not Critical. |
| [WEKAPP-577169](https://wekaio.atlassian.net/browse/WEKAPP-577169) | Auth CLI StdinReadlnError | **Major or Minor** | Component moved to Test; failure in non-interactive test setup. Test/infra issues → Major or Minor, not Critical. |
| [WEKAPP-591290](https://wekaio.atlassian.net/browse/WEKAPP-591290) | UpgradeFailed: verify no rebuild failed, drives0 timed out | **Major** | Initially assessed Critical (upgrade blocked). Re-evaluated: root cause is test timeout / lab conditions or correct product behavior. **Not all UpgradeFailed → Critical**; verify root cause before raising. |
| [WEKAPP-591313](https://wekaio.atlassian.net/browse/WEKAPP-591313) | CriticalEventException: CacheFlushHanging | **Major** | Initially assessed Critical (CriticalEvent). Re-evaluated: stayed Major. Root cause may be test-induced (e.g. mayhem/stress scenario) or narrow/edge condition. **Not all CriticalEvent → Critical**; verify whether it indicates general product defect. |
| [WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646) | ASSERT failed: FailedDisksTable[DiskId]=31 instead of 0 | **Major** | Initially assessed Critical (product ASSERT). Re-evaluated: stayed Major. Root cause may be test setup, cluster config, or fix was test/infra. **Not all ASSERT → Critical**; verify context (test-induced vs. genuine product defect). |
| [WEKAPP-568145](https://wekaio.atlassian.net/browse/WEKAPP-568145) | RealUpgradeException: buckets_list_statuses empty (after_upgrade) | **Major** | Initially assessed Critical (upgrade blocked). Re-evaluated: stayed Major. Failure in after_upgrade stage may be test assertion or test expectation, not product bug. **Upgrade failures in post-upgrade verification** — verify if product bug or test logic. |
| [WEKAPP-586233](https://wekaio.atlassian.net/browse/WEKAPP-586233) | SnapshotPolicyInvalidMonthDayValue: day 29 invalid | **Major** | Initially assessed Critical (scheduler correctness). Re-evaluated: stayed Major. Validation/scheduler bugs may be Major if low customer impact, design choice, or edge case. **Not all correctness bugs → Critical**; consider impact breadth. |

---

**Note on UpgradeFailed / upgrade blocked:** Not every UpgradeFailed or RealUpgradeException is automatically Critical. Distinguish:

- **Critical:** Product bug that blocks a **valid** upgrade (e.g. frontend init failure, clients not reaching UP, connection refused, version mismatch bug).
- **Major:** Test timeout, lab config (disk space, memory), **correct product behavior**, or **post-upgrade verification failure** (e.g. after_upgrade AssertionError may be test assertion, not product bug). Examples: [WEKAPP-591290](https://wekaio.atlassian.net/browse/WEKAPP-591290) (verify no rebuild), [WEKAPP-568145](https://wekaio.atlassian.net/browse/WEKAPP-568145) (buckets_list_statuses empty).

---

**Note on validation / scheduler correctness:** Bugs that affect correctness (e.g. snapshot policy, validation rules) are not automatically Critical. Consider **impact breadth**: if low customer impact, design choice, or edge case → **Major**. Example: [WEKAPP-586233](https://wekaio.atlassian.net/browse/WEKAPP-586233) (day 29 invalid) stayed Major.

---

**Note on CriticalEvent and ASSERT:** Not every CriticalEvent or ASSERT is automatically Critical. Verify root cause:

- **CriticalEvent** (CacheFlushHanging, DestageBlocked, etc.): **Critical** if it indicates a general product defect under normal/customer conditions. **Major** if test-induced (mayhem/stress), narrow scenario, or fix was test/infra. Example: [WEKAPP-591313](https://wekaio.atlassian.net/browse/WEKAPP-591313) (CacheFlushHanging) stayed Major.
- **ASSERT**: **Critical** if genuine product defect (e.g. wekanode crash, data path). **Major** if test setup induced it, fix was test/infra, or scenario is not customer-relevant. Example: [WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646) (FailedDisksTable ASSERT) stayed Major.
- **Product crash (SIGABRT/SIGSEGV)**: When it is a genuine product defect, stays **Critical**. Example: [WEKAPP-581666](https://wekaio.atlassian.net/browse/WEKAPP-581666) (wekanode SIGABRT) confirmed Critical after re-evaluation.

---

**Note on WEKAPP-579708 (S3 tag verification):** Initially assessed as Major due to S3 compliance. Per developer clarification: **S3 tags are metadata; metadata loss is treated the same as data loss** → **Critical** is correct. See Section 5.2, criterion 3 and the metadata loss clarification above.

---

## 5. Automation Bug / Test Component Guidance (new section)

**Section title:** ### Automation Bug / Test Component Guidance

---

For tickets typed as **Automation Bug** or where the component is **Test**:

- Severity should reflect **product impact**, not CI impact.
- A bug that blocks CI but has no customer or product impact → **Major** or **Minor**.
- If the root cause is in test design, environment, or infrastructure (e.g. timeout, non-interactive CLI invocation) → **Major** or **Minor**, even if it blocks other tests.

---

## 6. Re-evaluation Triggers (add to end of Section 6 – Decision Guide)

**Section title:** #### Re-evaluation Triggers

---

Re-evaluate severity when:

- **Root cause is confirmed** — Product bug vs. test/infra; adjust if the cause differs from initial triage.
- **Run frequency and failure rate are known** — Apply the Test Run Frequency section above.
- **Component is moved** — e.g. Control → Test; often indicates Major or Minor.
- **Failure is UpgradeFailed or RealUpgradeException** — Verify whether a product bug blocks a valid upgrade (→ Critical) or if root cause is test timeout, lab config, or correct product behavior (→ Major). See WEKAPP-591290 example.
- **Failure is CriticalEvent (e.g. CacheFlushHanging, DestageBlocked) or ASSERT in product code** — Do not assume CriticalEvent or ASSERT alone implies Critical. Re-check the root cause before raising severity:
  - **Critical** if it reflects a general product defect under normal or customer-relevant conditions: wekanode crash (SIGABRT/SIGSEGV), data path corruption, or a bug that would occur in a typical deployment.
  - **Major** if it was test-induced (mayhem/stress scenario, narrow cluster config), triggered by unusual setup, or the fix was in test/infra code. Ask: *"Would this occur in a typical customer deployment?"* — If no, consider Major.
  - Examples: [WEKAPP-591313](https://wekaio.atlassian.net/browse/WEKAPP-591313) (CacheFlushHanging stayed Major), [WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646) (FailedDisksTable ASSERT stayed Major), [WEKAPP-581666](https://wekaio.atlassian.net/browse/WEKAPP-581666) (wekanode SIGABRT confirmed Critical).

---

## 7. V4.4.6 Critical Automation Bugs – Severity Review

**Source JQL:** `project = WEKAPP AND issuetype = "Automation Bug" AND fixVersion = V4.4.6 AND status in (Done, Fixed) AND priority = Critical`

| Ticket | Component | Summary (short) | Severity OK? | Rationale |
|--------|-----------|-----------------|--------------|-----------|
| [WEKAPP-456816](https://wekaio.atlassian.net/browse/WEKAPP-456816) | Control / Authentication | RemoteException: Organization not found (API / user_list) during Mayhem test | **Consider Major** | API error during org creation in stress test. Root cause in Control/Auth. Product impact: org/user API can fail → affects multi-tenancy. **Critical defensible** if it blocks tenant ops; **Major** if rare/edge in stress. |
| [WEKAPP-472954](https://wekaio.atlassian.net/browse/WEKAPP-472954) | Platform / Network | wekanode SIGSEGV (core dump) with MIXED MTU | **Yes** | Core dump in wekanode = product crash. Per Critical criteria: unplanned node crash, severe availability impact. **Critical is correct.** |
| [WEKAPP-475458](https://wekaio.atlassian.net/browse/WEKAPP-475458) | Filesystem / RAID | allocationJob deadlock; ProcessTimedOut 12h; IOs hanging 3.5h+ | **Yes** | IO hang/deadlock blocks core storage path; DUDL risk when writes stall. **Critical is correct.** |
| [WEKAPP-479786](https://wekaio.atlassian.net/browse/WEKAPP-479786) | Control | Real upgrade validation failed: cleanup file `client_999_graceful_cluster_leave` failed | **Consider Major** | Upgrade validation failure during unmount/cleanup. Root cause may be test/infra (cleanup script). If product bug blocks upgrade → Critical; if test cleanup → **Major per Automation Bug guidance.** |
| [WEKAPP-480466](https://wekaio.atlassian.net/browse/WEKAPP-480466) | Upgrade / NDU | Upgrade failed: drives0 timed out – Not all drives unwritable | **Yes** | NDU upgrade blocked on supported scenario. Per criterion 2 (feature/deployment blocked) → **Critical is correct.** |
| [WEKAPP-482802](https://wekaio.atlassian.net/browse/WEKAPP-482802) | Control / Diags | index.json not found on Weka Home for hosts (diags collect when host down) | **Consider Major** | Diags test expectation when host unreachable. Likely test logic or timing, not core product failure. Per Automation Bug guidance → **Major if no customer impact.** |
| [WEKAPP-483165](https://wekaio.atlassian.net/browse/WEKAPP-483165) | Platform | GDS read command timed out after 1 day | **Consider Major** | Timeout in GDS test. Could be product hang or test timeout too low. If product hang → Critical; if test/infra timeout → **Major.** |
| [WEKAPP-483644](https://wekaio.atlassian.net/browse/WEKAPP-483644) | Filesystem / RAID | Allocation fiber hang; SIGABRT "diet required for PlacementSpaceN" | **Yes** | Core dump (SIGABRT) in RAID allocation path. Product crash, DUDL risk. **Critical is correct.** |
| [WEKAPP-485108](https://wekaio.atlassian.net/browse/WEKAPP-485108) | Filesystem / RAID / tests | HangingDriverIOException: 32/32 ops hanging ~10m (scrubber priorities) | **Yes** | All IOs hung; scrubber/RAID logic bug. Severe availability, DUDL risk. **Critical is correct.** |
| [WEKAPP-487979](https://wekaio.atlassian.net/browse/WEKAPP-487979) | Filesystem / File Logic | EOS results may be lost if revokeCapacityLease hangs; linkat EEXIST, CallFailed | **Yes** | Data integrity / EOS result loss risk. Per criterion 3 (DUDL) → **Critical is correct.** |
| [WEKAPP-488128](https://wekaio.atlassian.net/browse/WEKAPP-488128) | Platform / Reactor | CriticalEventException: AssertionFailed in reactor.d (relentless timer fiber) | **Yes** | AssertionFailed = product crash. **Critical is correct.** |
| [WEKAPP-488555](https://wekaio.atlassian.net/browse/WEKAPP-488555) | Filesystem / Data Reduction | DR: relocating blocks removes from ingest queue; blocks never ingested | **Yes** | Data reduction bug → data never properly ingested. DUDL/correctness risk. **Critical is correct.** |
| [WEKAPP-489826](https://wekaio.atlassian.net/browse/WEKAPP-489826) | Filesystem / Snapshots | snapdiff Count mismatch (records vs result_count) 250 vs 478 | **Yes** | Snapshot difflist inconsistency = metadata/correctness bug. Can affect backup/restore. **Critical defensible** if it causes wrong snapdiff results. |

**Summary:** 9 clearly Critical (product crash, DUDL, severe availability). 4 worth re-checking (456816, 479786, 482802, 483165) — may be Major if root cause is test/infra per Automation Bug guidance.

---

## 8. V5.0 Critical Automation Bugs – Severity Review

**Source JQL:** `project = WEKAPP AND issuetype = "Automation Bug" AND fixVersion = V5.0 AND status in (Done, Fixed) AND priority = Critical ORDER BY key ASC`

| Ticket | Component | Summary (short) | Severity OK? | Rationale |
|--------|-----------|-----------------|--------------|-----------|
| [WEKAPP-468350](https://wekaio.atlassian.net/browse/WEKAPP-468350) | Interfaces / Floating IP | NodeExceptionExit: Index/key not found in IpConfig (RangeError) | **Yes** | Product crash (RangeError) in networking config path. **Critical is correct.** |
| [WEKAPP-471714](https://wekaio.atlassian.net/browse/WEKAPP-471714) | Infra / Testlight | CoreFoundException: systemd-network core dump | **Consider Major** | systemd-network is OS/infra, not weka code. Per Automation Bug guidance, infra component → **Major** unless weka triggered it. |
| [WEKAPP-472954](https://wekaio.atlassian.net/browse/WEKAPP-472954) | Platform / Network | wekanode SIGSEGV (MIXED MTU) | **Yes** | Core dump in wekanode = product crash. **Critical is correct.** |
| [WEKAPP-480478](https://wekaio.atlassian.net/browse/WEKAPP-480478) | Infra / Classy | NotEnoughCapacityForFilesystems (capacity calc) | **Consider Major** | Classy = test infra. Capacity calc for test setup; likely test design, not product. **Major** if no customer impact. |
| [WEKAPP-480596](https://wekaio.atlassian.net/browse/WEKAPP-480596) | Infra | AttributeError: RebuildTracker no attribute 'progression_trackers' | **Consider Major** | Component = Infra; test/framework bug. **Major per Automation Bug guidance.** |
| [WEKAPP-485909](https://wekaio.atlassian.net/browse/WEKAPP-485909) | Upgrade / NDU | UpgradeFailed: drives0 timed out (No election for leader) | **Yes** | NDU upgrade blocked. Per criterion 2 → **Critical is correct.** |
| [WEKAPP-487996](https://wekaio.atlassian.net/browse/WEKAPP-487996) | Interfaces / S3-FE | AssertionError: bg.append.tmp MD5 mismatch (expected vs empty) | **Yes** | S3 background append integrity bug; data correctness risk. **Critical is correct.** |
| [WEKAPP-489200](https://wekaio.atlassian.net/browse/WEKAPP-489200) | Filesystem / RAID | StatLimitExceeded: INTERRUPTS scrubber (during teardown) | **Yes** | Critical event in RAID scrubber; stat limit exceeded = product behavior. **Critical is correct.** |
| [WEKAPP-489826](https://wekaio.atlassian.net/browse/WEKAPP-489826) | Filesystem / Snapshots | snapdiff Count mismatch (records vs result_count) | **Yes** | Snapshot difflist inconsistency. **Critical is correct.** |
| [WEKAPP-490719](https://wekaio.atlassian.net/browse/WEKAPP-490719) | Upgrade / NDU | UpgradeFailed: drives0 (NDU with --skip-rebuild-check) | **Yes** | NDU upgrade blocked. **Critical is correct.** |
| [WEKAPP-491461](https://wekaio.atlassian.net/browse/WEKAPP-491461) | Control / Leadership, Upgrade | ProcessTimedOut: prepare_leader_for_upgrade status command 5m | **Consider Major** | Process timeout during upgrade prepare. If product hang → Critical; if test timeout/env → **Major.** |
| [WEKAPP-491782](https://wekaio.atlassian.net/browse/WEKAPP-491782) | Clustering / Container | ContainerStillReportedAsAlive after weka local restart | **Yes** | Container state inconsistency; agent reports wrong state. Reliability/cluster mgmt bug. **Critical defensible.** |
| [WEKAPP-492147](https://wekaio.atlassian.net/browse/WEKAPP-492147) | Platform / Network | wekanode SIGSEGV (RDMA restart manhole null pointer) | **Yes** | Core dump in wekanode. **Critical is correct.** |
| [WEKAPP-494623](https://wekaio.atlassian.net/browse/WEKAPP-494623) | Upgrade / NDU / tests | ASSERT: FSCK signature mismatch, upgrade doesn't wait for leader | **Yes** | Upgrade logic bug; ASSERT = product defect. **Critical is correct.** |
| [WEKAPP-494662](https://wekaio.atlassian.net/browse/WEKAPP-494662) | Interfaces / S3-FE | UpgradeFailed: Failed to prepare dependent containers 0/1 | **Yes** | Upgrade blocked; S3 prep failure. **Critical is correct.** |
| [WEKAPP-494703](https://wekaio.atlassian.net/browse/WEKAPP-494703) | Platform / Network | GDS read Connection timed out (RDMA completion timeout too short) | **Yes** | Product config/timeout too short for GDS; blocks large read. **Critical is correct.** |
| [WEKAPP-494846](https://wekaio.atlassian.net/browse/WEKAPP-494846) | Control / Leadership | Snapshot deletion slower; FS capacity did not decrease (1h timeout) | **Consider Major** | Timeout in test expectation (capacity decrease). If product regression → Critical; if test timing → **Major.** |
| [WEKAPP-494867](https://wekaio.atlassian.net/browse/WEKAPP-494867) | Filesystem / Squelch | Digest Block Prefix Mismatch (RAID PrefixMismatch) | **Yes** | RAID read integrity failure; data corruption risk. **Critical is correct.** |
| [WEKAPP-495224](https://wekaio.atlassian.net/browse/WEKAPP-495224) | Interfaces / Driver | CommandTimeoutError: mount timed out 1h (setup) | **Consider Major** | Mount timeout during setup. If product hang → Critical; if test/env → **Major.** |
| [WEKAPP-495667](https://wekaio.atlassian.net/browse/WEKAPP-495667) | Control / nginx | NodeExceptionExit: Range violation (algorithm/iteration.d) | **Yes** | Product crash (RangeError). **Critical is correct.** |
| [WEKAPP-499292](https://wekaio.atlassian.net/browse/WEKAPP-499292) | Mount / Agent | Mount: Some containers did not become ready (4.4.6 mixed clients) | **Yes** | Deployment/ready check blocked. **Critical defensible.** |
| [WEKAPP-499721](https://wekaio.atlassian.net/browse/WEKAPP-499721) | Upgrade / NDU / tests | UpgradeFailed: ERROR_CONTAINER_IN_DIFFERENT_SOURCE_VERSION | **Yes** | Upgrade flow bug; version mismatch. **Critical is correct.** |
| [WEKAPP-499731](https://wekaio.atlassian.net/browse/WEKAPP-499731) | Upgrade / NDU | UpgradeFailed: machine with 2 compute containers | **Yes** | NDU upgrade blocked. **Critical is correct.** |
| [WEKAPP-499884](https://wekaio.atlassian.net/browse/WEKAPP-499884) | Interfaces / Driver | AssertionError: Different versions found (upgrade cancel during prepare) | **Yes** | Upgrade state/version consistency bug. **Critical is correct.** |
| [WEKAPP-501577](https://wekaio.atlassian.net/browse/WEKAPP-501577) | Filesystem / File Locks | AssertionFailed: timer double-cancel (flock) | **Yes** | Product assert in file locks. **Critical is correct.** |
| [WEKAPP-502905](https://wekaio.atlassian.net/browse/WEKAPP-502905) | Platform / Network | AssertionFailed: Node cannot reject itself (DATA_WITH_WRONG_SECRET) | **Yes** | Product assert; fencing/consistency. **Critical is correct.** |
| [WEKAPP-504493](https://wekaio.atlassian.net/browse/WEKAPP-504493) | Control / Raft | TalkerProcessLineTimedOut 1h (raft_st... command) | **Consider Major** | Command timeout in Raft test. If product hang → Critical; if test → **Major.** |
| [WEKAPP-506524](https://wekaio.atlassian.net/browse/WEKAPP-506524) | Control / API | AssertionError: REST API vs JRPC FD count mismatch | **Yes** | API consistency bug; affects management correctness. **Critical defensible.** |
| [WEKAPP-506618](https://wekaio.atlassian.net/browse/WEKAPP-506618) | Upgrade / NDU | AssertionError: Failed to build after freezing ref types | **Consider Major** | Build/freeze failure; component NDU. Could be test/build infra → **Major** if no runtime impact. |
| [WEKAPP-508564](https://wekaio.atlassian.net/browse/WEKAPP-508564) | Control | slice extends past array – ProcessExecutionError (weka fs) | **Yes** | Product crash (array bounds); core.exception. **Critical is correct.** |
| [WEKAPP-510331](https://wekaio.atlassian.net/browse/WEKAPP-510331) | Filesystem / Audit | AssertionError: Failed to find traces (big filenames) | **Consider Major** | Audit trace test assertion. If product audit bug → Critical; if test expectation → **Major.** |
| [WEKAPP-510736](https://wekaio.atlassian.net/browse/WEKAPP-510736) | Filesystem / Audit | AssertionError: Failed to find traces Create file (big filename) | **Consider Major** | Same as above; audit trace. **Major if test-only.** |
| [WEKAPP-512768](https://wekaio.atlassian.net/browse/WEKAPP-512768) | Upgrade / NDU / tests | RealUpgradeException: context deadline exceeded (prepare_version) | **Yes** | Upgrade blocked; prepare timeout. **Critical is correct.** |
| [WEKAPP-514057](https://wekaio.atlassian.net/browse/WEKAPP-514057) | Filesystem / RAID | PredicateNotSatisfied: Disks still rebuilding (narrow cluster) | **Yes** | Rebuild stuck; DUDL/availability risk. **Critical is correct.** |
| [WEKAPP-514322](https://wekaio.atlassian.net/browse/WEKAPP-514322) | Interfaces / S3-FE | UpgradeFailed: s3 timed out in WAITING_FOR_READY_TO_UPGRADE | **Yes** | NDU blocked; S3 container not ready. **Critical is correct.** |
| [WEKAPP-514600](https://wekaio.atlassian.net/browse/WEKAPP-514600) | Platform / SSD | NodeSignalExit SIGFPE | **Yes** | Product crash (SIGFPE). **Critical is correct.** |
| [WEKAPP-515379](https://wekaio.atlassian.net/browse/WEKAPP-515379) | Platform / tests | ProcessExecutionError: Authentication error (recovery script) | **Consider Major** | Component = tests; script/auth in test. **Major per Automation Bug guidance.** |
| [WEKAPP-515784](https://wekaio.atlassian.net/browse/WEKAPP-515784) | Interfaces / Driver / tests | FileNotFoundError: No such file (rtfs_sandbox path) | **Consider Major** | Component = Driver/tests; path not found in test. **Major if test logic.** |
| [WEKAPP-516585](https://wekaio.atlassian.net/browse/WEKAPP-516585) | Filesystem / RAID / tests | Exception: ClusterInfo no member firstBulkyPlacementIdx | **Consider Major** | Component = tests; test/framework compatibility. **Major.** |
| [WEKAPP-516668](https://wekaio.atlassian.net/browse/WEKAPP-516668) | Infra / Installation | Version already downloaded (weka local setup) | **Consider Major** | Infra/Installation; version already present. Likely test setup, not product. **Major.** |
| [WEKAPP-516710](https://wekaio.atlassian.net/browse/WEKAPP-516710) | Filesystem / RAID | NotEnoughMemoryForRAIDOperationOnFirstStartIO | **Yes** | Cluster init blocked; memory requirement. **Critical is correct** (deployment blocked). |
| [WEKAPP-517776](https://wekaio.atlassian.net/browse/WEKAPP-517776) | Upgrade / NDU | BuildException: Error in 'Build' phase (packaging) | **Consider Major** | Packaging/build failure. If blocks release → Critical; if CI/build → **Major.** |
| [WEKAPP-518091](https://wekaio.atlassian.net/browse/WEKAPP-518091) | Control / Agent | Containers did not stop in time (weka local restart test) | **Consider Major** | Test expectation (stop timeout). **Major if test timing.** |
| [WEKAPP-518351](https://wekaio.atlassian.net/browse/WEKAPP-518351) | Upgrade / NDU / tests | ProcessExecutionError: weka debug upgrade – Please pass type or --all | **Consider Major** | Component = tests; CLI invocation in test. **Major.** |
| [WEKAPP-518598](https://wekaio.atlassian.net/browse/WEKAPP-518598) | Infra / Testlight | logrotate core dump (non-weka-code) | **Consider Major** | Non-weka core dump; OS/infra. **Major.** |
| [WEKAPP-518801](https://wekaio.atlassian.net/browse/WEKAPP-518801) | Upgrade / NDU | UpgradeFailed: verification not all hosts up – context deadline exceeded | **Yes** | Upgrade verification failed. **Critical is correct.** |
| [WEKAPP-519052](https://wekaio.atlassian.net/browse/WEKAPP-519052) | Control / Traces / WTracer | wekanode.assert: const(TscTimePoint) | **Yes** | Product assert in tracer. **Critical is correct.** |
| [WEKAPP-519448](https://wekaio.atlassian.net/browse/WEKAPP-519448) | Devops / Build | BuildException: Error in 'Build' phase | **Consider Major** | Build/packaging; Devops. **Major** (CI impact, not runtime). |
| [WEKAPP-519476](https://wekaio.atlassian.net/browse/WEKAPP-519476) | Upgrade / NDU / tests | UpgradeFailed: failed to fetch auto core allocated container list | **Yes** | Upgrade verification; fetch failed. **Critical is correct.** |
| [WEKAPP-519655](https://wekaio.atlassian.net/browse/WEKAPP-519655) | Platform / SSD | ASSERT failed: must be called from main thread (nvme_ctrlr) | **Yes** | Product assert; threading bug. **Critical is correct.** |
| [WEKAPP-520843](https://wekaio.atlassian.net/browse/WEKAPP-520843) | Filesystem / RAID | 1hop write after placement switch: FoundCorruptedBlockInStripe | **Yes** | RAID data integrity; corrupted block in stripe. **Critical is correct.** |
| [WEKAPP-522813](https://wekaio.atlassian.net/browse/WEKAPP-522813) | Filesystem / RAID | NodeExceptionExit: Too many errors (static_hash.d) | **Yes** | Product crash/exception in RAID path. **Critical is correct.** |
| [WEKAPP-525759](https://wekaio.atlassian.net/browse/WEKAPP-525759) | Filesystem / Squelch | NDU causes double-free Digest Block (AssertionFailed PlacementDesc) | **Yes** | Product assert; double-free in NDU. **Critical is correct.** |
| [WEKAPP-528679](https://wekaio.atlassian.net/browse/WEKAPP-528679) | Platform / tests | SsdProxyPIDWasChanged – ssd_proxy crashed/restarted | **Yes** | SSD proxy process crash; platform reliability. **Critical is correct.** |
| [WEKAPP-529391](https://wekaio.atlassian.net/browse/WEKAPP-529391) | Interfaces / S3-FE | AssertionFailed: static_hash.d ItemsRange (S3) | **Yes** | Product assert in S3 path. **Critical is correct.** |
| [WEKAPP-530765](https://wekaio.atlassian.net/browse/WEKAPP-530765) | Platform / Network | ASSERT failed: RDMA BADCSUM h/w vs CPU checksum mismatch | **Yes** | RDMA integrity/correctness bug. **Critical is correct.** |
| [WEKAPP-530836](https://wekaio.atlassian.net/browse/WEKAPP-530836) | Filesystem / Infrastructure | AssertionFailed: static_hash.d allocCell | **Yes** | Product assert. **Critical is correct.** |
| [WEKAPP-532509](https://wekaio.atlassian.net/browse/WEKAPP-532509) | Control / Config | ASSERT: BucketsMapCache not ready (leadership_maps.d) | **Yes** | Product assert in config/leadership. **Critical is correct.** |
| [WEKAPP-532524](https://wekaio.atlassian.net/browse/WEKAPP-532524) | Clustering / Versioning | UnicodeDecodeError: ascii can't decode byte | **Consider Major** | Test/framework encoding in versioning. **Major** if test logic. |
| [WEKAPP-532566](https://wekaio.atlassian.net/browse/WEKAPP-532566) | Platform / SSD | Cluster init failed: NotEnoughFailureDomainsWithWorkingDrives | **Yes** | Cluster init blocked; hardware/start-io. **Critical is correct.** |
| [WEKAPP-532603](https://wekaio.atlassian.net/browse/WEKAPP-532603) | Filesystem / RAID | ASSERT: non-existing placement BucketId (distribution_cache.d) | **Yes** | Product assert in RAID distribution. **Critical is correct.** |
| [WEKAPP-533153](https://wekaio.atlassian.net/browse/WEKAPP-533153) | Infra | ContainersStillStoppingNotRemoved (teardown) | **Consider Major** | Teardown timeout; containers not stopped. **Major** if test/env timing. |
| [WEKAPP-533780](https://wekaio.atlassian.net/browse/WEKAPP-533780) | Interfaces / Driver / tests | FioException: stat: No such file or directory | **Consider Major** | FIO/path in test. **Major** if test logic. |
| [WEKAPP-533904](https://wekaio.atlassian.net/browse/WEKAPP-533904) | Infra / Testlight / Plugins | KeyError: 'ssd_proxy_pid_tracker' (setup) | **Consider Major** | Test plugin/setup bug. **Major per Automation Bug guidance.** |
| [WEKAPP-535255](https://wekaio.atlassian.net/browse/WEKAPP-535255) | Control | ProcessExecutionError: KMS vault Key not found (setup) | **Consider Major** | KMS/vault setup; test env config. **Major** if no product bug. |
| [WEKAPP-535456](https://wekaio.atlassian.net/browse/WEKAPP-535456) | Devops / Lab / OCI | Mount: Could not connect to any backend (setup) | **Consider Major** | Mount during lab setup; env/connectivity. **Major** if infra. |
| [WEKAPP-537180](https://wekaio.atlassian.net/browse/WEKAPP-537180) | Filesystem / RAID | ScrubberHanging: ScrubPlacement 2400s (relocate starved) | **Yes** | Critical event; scrubber hang. **Critical is correct.** |
| [WEKAPP-537489](https://wekaio.atlassian.net/browse/WEKAPP-537489) | Control / API | HttpServerFibersExhausted (APIs hang on down buckets) | **Yes** | API hang; management inaccessibility. **Critical is correct.** |
| [WEKAPP-539869](https://wekaio.atlassian.net/browse/WEKAPP-539869) | Filesystem / Snapshots | single hop write journal ASSERT – Extent not found on replay | **Yes** | Product assert; snapshot/journal consistency. **Critical is correct.** |
| [WEKAPP-541238](https://wekaio.atlassian.net/browse/WEKAPP-541238) | Control | RealUpgradeException: verification not all hosts up – deadline exceeded | **Yes** | Upgrade verification failed. **Critical is correct.** |
| [WEKAPP-541420](https://wekaio.atlassian.net/browse/WEKAPP-541420) | Platform / SSD | wekanode SIGABRT at weka/ssd/service.d | **Yes** | Product crash (SIGABRT). **Critical is correct.** |
| [WEKAPP-542251](https://wekaio.atlassian.net/browse/WEKAPP-542251) | Infra / Installation | ProcessExecutionError: curl install script (retcode=2) | **Consider Major** | Install script curl failure; lab/network. **Major** if env. |
| [WEKAPP-542625](https://wekaio.atlassian.net/browse/WEKAPP-542625) | Filesystem | AssertionError: single-hop write percent < 95% | **Consider Major** | Test assertion on 1hop write rate. If product regression → Critical; if test threshold → **Major.** |
| [WEKAPP-544166](https://wekaio.atlassian.net/browse/WEKAPP-544166) | Control | TalkerServerTimeout x7: agent did not receive command 20m | **Consider Major** | Talker timeout in test. **Major** if test/agent env. |
| [WEKAPP-544477](https://wekaio.atlassian.net/browse/WEKAPP-544477) | Control / Agent / Tests | [TestRebootDrainedStatus] TimeoutException: Container states DRAINED/STOP | **Consider Major** | Test expectation during reboot. **Major** if test timing. |
| [WEKAPP-545516](https://wekaio.atlassian.net/browse/WEKAPP-545516) | Clustering / Requested actions | AssertionFailed: mmap_backed.d MmapBacked | **Yes** | Product assert. **Critical is correct.** |
| [WEKAPP-545744](https://wekaio.atlassian.net/browse/WEKAPP-545744) | Control / Raft | WekanodeUTFailed: unit tests failed | **Yes** | wekanode UT failure = product defect. **Critical is correct.** |
| [WEKAPP-546740](https://wekaio.atlassian.net/browse/WEKAPP-546740) | Interfaces / Driver | RealUpgradeException: frontend0 timed out, connection refused | **Yes** | Upgrade blocked. **Critical is correct.** |
| [WEKAPP-547725](https://wekaio.atlassian.net/browse/WEKAPP-547725) | Interfaces / Driver | HangingDriverIOException: 217/218 ops hanging ~10m (deadlock upgrade) | **Yes** | Driver hang; severe availability. **Critical is correct.** |
| [WEKAPP-550685](https://wekaio.atlassian.net/browse/WEKAPP-550685) | Interfaces / Driver | NodeExceptionExit: Device or resource busy | **Yes** | Product exception in driver. **Critical is correct.** |
| [WEKAPP-550758](https://wekaio.atlassian.net/browse/WEKAPP-550758) | Infra | TypeError: float - NoneType (setup) | **Consider Major** | Test/framework bug in setup. **Major per Automation Bug guidance.** |
| [WEKAPP-552384](https://wekaio.atlassian.net/browse/WEKAPP-552384) | Filesystem / Relocate | ScrubberHanging: relocateBlocks, ScrubPlacement 2400s | **Yes** | Critical event; scrubber hang. **Critical is correct.** |
| [WEKAPP-557241](https://wekaio.atlassian.net/browse/WEKAPP-557241) | Devops / Lab / Networking | curl Failed writing body (S3 download) | **Consider Major** | Lab/network curl failure. **Major** if infra. |
| [WEKAPP-557544](https://wekaio.atlassian.net/browse/WEKAPP-557544) | Upgrade / NDU / tests | RealUpgradeException: insufficient disk space on host | **Yes** | Upgrade verification; disk space. **Critical** if product; **Major** if lab config. |
| [WEKAPP-560170](https://wekaio.atlassian.net/browse/WEKAPP-560170) | Control / Agent, Interfaces / SMBW | ProcessExecutionError: weka local restart smbw (dependent containers) | **Consider Major** | Restart command in test; dependent containers. **Major** if test flow. |
| [WEKAPP-560546](https://wekaio.atlassian.net/browse/WEKAPP-560546) | Upgrade / NDU | RealUpgradeException: containers with auto core allocation | **Yes** | Upgrade blocked; dedicated core check. **Critical is correct.** |
| [WEKAPP-562894](https://wekaio.atlassian.net/browse/WEKAPP-562894) | Platform / tests | FailedJobsException: GoaderLoader jobs failed | **Consider Major** | Platform tests; job failure. **Major** if test/infra. |
| [WEKAPP-563423](https://wekaio.atlassian.net/browse/WEKAPP-563423) | Infra / Installation | wekanode SIGABRT at weka/cluster/node.d | **Yes** | Product crash (SIGABRT). **Critical is correct.** |
| [WEKAPP-567938](https://wekaio.atlassian.net/browse/WEKAPP-567938) | DevOps | [container didnt join in time] ContainerDidNotReceiveName | **Consider Major** | Container join timing during install. **Major** if lab/env. |
| [WEKAPP-569623](https://wekaio.atlassian.net/browse/WEKAPP-569623) | Filesystem / Snapshots / tests | TimeoutException: snapshot delete did not start | **Consider Major** | Snapshot delete timeout in test. **Major** if test timing. |
| [WEKAPP-582610](https://wekaio.atlassian.net/browse/WEKAPP-582610) | Devex / CI | FailedToBuildRpcContainer (setup) | **Consider Major** | CI/RPC container build. **Major** if Devex/CI infra. |

**Summary:** 55 clearly Critical (product crash, DUDL, upgrade blocked, ASSERT, scrubber hang, driver hang). 36 worth re-checking — may be Major if root cause is test/infra/env per Automation Bug guidance. Total: 91 tickets.

---

## Quick copy blocks (plain text, no formatting)

Use these if Notion strips formatting:

---

**Metadata loss block:**
```
Metadata loss (including S3 object tags): Loss or incorrect handling of metadata such as S3 object tags is treated the same as data loss for severity classification. Tags affect lifecycle, retention, access control, and compliance; metadata loss can lead to data loss or inaccessibility and is therefore at least Critical.
```

---

**Test Run Frequency block:**
```
Rare tests (run less than once per week): A failure is considered "interesting" — it may indicate a regression, flakiness, or environment issue. Many reproductions across runs increase the likelihood that the issue is Critical and should be prioritized.

Frequent tests (run more than once per week): If the failure rate is ~20% or higher, the GL/TL should supply explicit answers: root cause, severity rationale, and residual risk.

Note: Run frequency and failure rate influence priority and investigation focus. Severity (Critical / Major / Minor) is still driven by product impact per the formal definitions above.
```

---

**Automation Bug block:**
```
For tickets typed as Automation Bug or where the component is Test: Severity should reflect product impact, not CI impact. A bug that blocks CI but has no customer or product impact → Major or Minor. If the root cause is in test design, environment, or infrastructure (e.g. timeout, non-interactive CLI invocation) → Major or Minor, even if it blocks other tests.
```

---

**Re-evaluation Triggers block:**
```
Re-evaluate severity when: Root cause is confirmed — Product bug vs. test/infra; adjust if the cause differs from initial triage. Run frequency and failure rate are known — Apply the Test Run Frequency section above. Component is moved — e.g. Control → Test; often indicates Major or Minor.
```


---

## Regression from previous release — severity review

*Source CSV:* `regression_from_previous_release_minor (JIRA).csv` (JIRA export).

**Source:** [regression_from_previous_release_minor (JIRA).csv](/Users/alon.gilat/Downloads/regression_from_previous_release_minor%20(JIRA).csv)  
**Criteria:** Bug Severity Definition – Weka.io (Notion doc)

---

| Ticket | Summary (short) | Current Severity | Proposed Severity | Explanation |
|--------|-----------------|------------------|-------------------|-------------|
| [WEKAPP-591892](https://wekaio.atlassian.net/browse/WEKAPP-591892) | PortTestFailed: Port test nightly[gcp] failed | Major | **Major** | Port test = infra/test failure. Per Automation Bug guidance: blocks CI but no product semantics bug → **Major**. |
| [WEKAPP-591828](https://wekaio.atlassian.net/browse/WEKAPP-591828) | PortTestFailed: Port test nightly[gcp] on cluster failed | Blocker | **Major** | Same as above. Port test failure = test/infra. Per doc: severity reflects product impact, not CI impact. **Major**. |
| [WEKAPP-591750](https://wekaio.atlassian.net/browse/WEKAPP-591750) | HangingDriverIOException: 1/1 ops hanging ~10m | Major | **Critical** | Driver hang = severe availability, DUDL risk. Per criterion 3 (DUDL) and 4 (availability) → **Critical**. |
| [WEKAPP-591707](https://wekaio.atlassian.net/browse/WEKAPP-591707) | ClientsNotUpgraded: Some clients aren't 'UP' after upgrade | Critical | **Critical** | Upgrade blocked; clients don't reach UP. Per criterion 2 (deployment blocked) → **Critical is correct.** |
| [WEKAPP-591693](https://wekaio.atlassian.net/browse/WEKAPP-591693) | RealUpgradeException: 4.4.10.200 -> 4.4.11 (packaging) | Critical | **Consider Major** | Packaging phase upgrade failure. If product bug blocks upgrade → Critical; if build/packaging infra → **Major** per Automation Bug guidance. Re-check root cause. |
| [WEKAPP-591672](https://wekaio.atlassian.net/browse/WEKAPP-591672) | ProcessExecutionError: Temporary failure in name resolution | Major | **Major** | DNS/network failure in test. Env/network, not product. Per Automation Bug guidance → **Major**. |
| [WEKAPP-591660](https://wekaio.atlassian.net/browse/WEKAPP-591660) | AssertionError: Unexpected active overrides (BucketId INVALID) | Major | **Consider** | Assertion in config/overrides. If product bug in config path → Critical; if test expectation or config setup → **Major**. Re-check root cause. |
| [WEKAPP-591600](https://wekaio.atlassian.net/browse/WEKAPP-591600) | AssertionError: Unexpected active overrides | Major | **Consider** | Same as 591660. Verify if product config bug or test assertion. |
| [WEKAPP-591582](https://wekaio.atlassian.net/browse/WEKAPP-591582) | ExpectedEventDidNotOccur: NodeTraceback (teardown) | Major | **Major** | Phase = teardown; test expectation (expected event did not occur). Per Automation Bug guidance → **Major**. |
| [WEKAPP-591366](https://wekaio.atlassian.net/browse/WEKAPP-591366) | AssertionError: failure_domain_name Expected str!=Actual NoneType | Major | **Major** | Test assertion on field verification. If product bug → Critical; if test expectation → **Major**. Default **Major** until root cause known. |
| [WEKAPP-591331](https://wekaio.atlassian.net/browse/WEKAPP-591331) | TalkerProcessLineTimedOut: Command did not send output 5m | Major | **Major** | Talker timeout. Per doc: if product hang → Critical; if test/agent env → **Major**. Default **Major** until root cause known. |
| [WEKAPP-591290](https://wekaio.atlassian.net/browse/WEKAPP-591290) | UpgradeFailed: verify no rebuild failed, drives0 timed out | Major | **Major** | Per doc (WEKAPP-591290 example): re-evaluated, stayed Major. Root cause = test timeout / lab / correct product behavior. **Major is correct.** |
| [WEKAPP-591281](https://wekaio.atlassian.net/browse/WEKAPP-591281) | OSError: [Errno 5] Input/output error | Major | **Consider** | I/O error could be product (storage path) or env/hardware. Re-check root cause. |
| [WEKAPP-591254](https://wekaio.atlassian.net/browse/WEKAPP-591254) | ExceptionNotRaised: Did not raise ProcessExecutionError as expected | Blocker | **Major** | Test expectation (negative test). Per doc: ExceptionNotRaised = test logic → **Major**, not Critical. |
| [WEKAPP-591249](https://wekaio.atlassian.net/browse/WEKAPP-591249) | AssertionError: Unexpected lock type | Major | **Consider** | Per doc: if product lock logic bug → Critical; if test expectation → **Major**. Re-check root cause. |
| [WEKAPP-591236](https://wekaio.atlassian.net/browse/WEKAPP-591236) | weka: command not found (setup) | Major | **Major** | Phase = setup; weka not in PATH. Env/setup. Per Automation Bug guidance → **Major**. |
| [WEKAPP-591215](https://wekaio.atlassian.net/browse/WEKAPP-591215) | Mount: mount.nfs: NFS version or transport not supported | Major | **Consider** | NFS mount failure. If product protocol bug → Critical; if client/env config → **Major**. Per doc → re-check root cause. |
| [WEKAPP-590187](https://wekaio.atlassian.net/browse/WEKAPP-590187) | Mount: Some containers did not become ready (setup) | Major | **Major** | Phase = setup; containers not ready. Per Automation Bug guidance → **Major**. |
| [WEKAPP-589025](https://wekaio.atlassian.net/browse/WEKAPP-589025) | NodeSignalExit: signum=11 (SIGSEGV) | Major | **Critical** | Product crash (SIGSEGV). Per criterion 1: unplanned node crash → **Critical**. |
| [WEKAPP-584037](https://wekaio.atlassian.net/browse/WEKAPP-584037) | DidNotReachStatus: node did not reach UP, still DOWN | Major | **Major** | Node stayed DOWN. If product bug → Critical; if test/env → **Major**. Default **Major** until root cause known. |
| [WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646) | ASSERT failed: FailedDisksTable[DiskId]=31 instead of 0 | Major | **Major** | Per doc (WEKAPP-569646 example): re-evaluated, stayed Major. Root cause = test-induced or fix was test/infra. **Major is correct.** |
| [WEKAPP-568145](https://wekaio.atlassian.net/browse/WEKAPP-568145) | RealUpgradeException: buckets_list_statuses empty (after_upgrade) | Major | **Major** | Per doc (WEKAPP-568145 example): re-evaluated, stayed Major. Post-upgrade verification may be test assertion. **Major is correct.** |
| [WEKAPP-560629](https://wekaio.atlassian.net/browse/WEKAPP-560629) | ExceptionNotRaised: Did not raise ProcessExecutionError as expected | Critical | **Major** | Test expectation (negative test). Per doc: ExceptionNotRaised = test logic → **Major**. **Consider lowering from Critical to Major.** |

---

## Summary

| Category | Count |
|----------|-------|
| **Keep / Correct** (no change needed) | 15 |
| **Propose Critical** (raise from Major) | 2 (591750, 589025) |
| **Propose Major** (lower from Blocker/Critical) | 3 (591828, 591254, 560629) |
| **Consider** (re-check root cause before changing) | 6 |

---

## Key recommendations

- **Raise to Critical:** WEKAPP-591750 (HangingDriverIO), WEKAPP-589025 (SIGSEGV).
- **Lower to Major:** WEKAPP-591828 (Port test Blocker→Major), WEKAPP-591254 (ExceptionNotRaised Blocker→Major), WEKAPP-560629 (ExceptionNotRaised Critical→Major).
- **Re-check before changing:** WEKAPP-591693, 591660, 591600, 591281, 591249, 591215.

---

## Regression unhandled issues — severity review

*Source CSV:* `regression_unhandled_issues_minor_product (JIRA).csv` (JIRA export).

**Note:** For WEKAPP-591290, 591313, 569646, 568145, 586233, apply [Reconciled guidance](#reconciled-guidance-audits-vs-notion-misclassification-examples); the detailed “Critical” subsections below reflect the earlier audit voice and are partly superseded for those keys.

**Source:** [regression_unhandled_issues_minor_product (JIRA).csv](/Users/alon.gilat/Downloads/regression_unhandled_issues_minor_product%20(JIRA).csv)  
**Criteria:** Bug Severity Definition – Weka.io (Critical: product crash, ASSERT, DUDL, upgrade blocked, CriticalEvent)

---

| # | Ticket | Summary (short) | Current Priority | Critical? | Rationale |
|---|--------|-----------------|------------------|-----------|-----------|
| 1 | [WEKAPP-591828](https://wekaio.atlassian.net/browse/WEKAPP-591828) | PortTestFailed: Port test nightly[gcp] on cluster failed | Blocker | **No** | Port test = infra/test failure. Blocks CI but no product semantics bug. Per Automation Bug guidance → **Major**, not Critical. |
| 2 | [WEKAPP-591769](https://wekaio.atlassian.net/browse/WEKAPP-591769) | AssertionFailed: weka/network/lowlevel/mbuf.d MBufPool decref | Major | **Yes** | Product ASSERT in wekanode. Per Critical criteria: ASSERT in product code → **Critical**. |
| 3 | [WEKAPP-591744](https://wekaio.atlassian.net/browse/WEKAPP-591744) | ValueError: not enough values to unpack (expected 1, got 0) | Major | **No** | Python/test framework exception. Root cause in test code, not product. **Major** per Automation Bug guidance. |
| 4 | [WEKAPP-591736](https://wekaio.atlassian.net/browse/WEKAPP-591736) | while installing: TaskRunTimeoutError: Scope timed out 120s | Major | **No** | Phase = installing; timeout during setup. Test/env timing. **Major** per Automation Bug guidance. |
| 5 | [WEKAPP-591707](https://wekaio.atlassian.net/browse/WEKAPP-591707) | ClientsNotUpgraded: Some clients aren't 'UP' after weka local upgrade | Major | **Yes** | Upgrade blocked; clients don't reach UP after upgrade. Per criterion 2 (deployment blocked) → **Critical**. |
| 6 | [WEKAPP-591692](https://wekaio.atlassian.net/browse/WEKAPP-591692) | can't debug dpdk lock – lsof missing in runtime container | Major | **No** | Dev/debug tooling; lsof missing for debugging. No product runtime impact. **Major** or Minor. |
| 7 | [WEKAPP-591672](https://wekaio.atlassian.net/browse/WEKAPP-591672) | ProcessExecutionError: Temporary failure in name resolution (weka cluster host) | Major | **No** | DNS/network failure in test. Env/network, not product. **Major** per Automation Bug guidance. |
| 8 | [WEKAPP-591655](https://wekaio.atlassian.net/browse/WEKAPP-591655) | wekanode.assert: unimprintFib called in stem mode (management/client.d) | Major | **Yes** | Product ASSERT in wekanode. **Critical is correct.** |
| 9 | [WEKAPP-591617](https://wekaio.atlassian.net/browse/WEKAPP-591617) | wekanode.assert: weka/fs/entrypoint/read.d – ASSERT failed Netbuf | Major | **Yes** | Product ASSERT in filesystem read path. **Critical is correct.** |
| 10 | [WEKAPP-591591](https://wekaio.atlassian.net/browse/WEKAPP-591591) | CoreFoundException: Found new core dump: ganesha | Major | **Yes** | Ganesha = Weka NFS component. Core dump in product-related code → **Critical**. (If non-weka ganesha, re-check.) |
| 11 | [WEKAPP-591590](https://wekaio.atlassian.net/browse/WEKAPP-591590) | RealUpgradeException: frontend0 timed out, connection refused | Major | **Yes** | Upgrade blocked; frontend init failed. Per criterion 2 → **Critical**. |
| 12 | [WEKAPP-591388](https://wekaio.atlassian.net/browse/WEKAPP-591388) | while setup: NodeIsNotUp – node is DOWN | Major | **No** | Phase = setup; node down during test setup. Env/setup. **Major** per Automation Bug guidance. |
| 13 | [WEKAPP-591331](https://wekaio.atlassian.net/browse/WEKAPP-591331) | TalkerProcessLineTimedOut: Command did not send output 5m | Major | **No** | Talker timeout. If product hang → Critical; if test/agent env → **Major**. Default **Major** until root cause known. |
| 14 | [WEKAPP-591313](https://wekaio.atlassian.net/browse/WEKAPP-591313) | CriticalEventException: CacheFlushHanging | Major | **Yes** | Critical event; cache flush hanging. Severe availability, DUDL risk. **Critical is correct.** |
| 15 | [WEKAPP-591290](https://wekaio.atlassian.net/browse/WEKAPP-591290) | UpgradeFailed: verify no rebuild failed, drives0 timed out | Major | **Yes** | Upgrade blocked; verify no rebuild failed. **Critical is correct.** |
| 16 | [WEKAPP-591284](https://wekaio.atlassian.net/browse/WEKAPP-591284) | ExceptionNotRaised: Did not raise ProcessExecutionError as expected | Major | **No** | Test expectation (negative test – expected error did not occur). Test logic. **Major** per Automation Bug guidance. |
| 17 | [WEKAPP-591249](https://wekaio.atlassian.net/browse/WEKAPP-591249) | AssertionError: Unexpected lock type | Major | **Consider** | Assertion in test or product. If product lock logic bug → Critical; if test expectation → **Major**. Re-check root cause. |
| 18 | [WEKAPP-591229](https://wekaio.atlassian.net/browse/WEKAPP-591229) | CriticalEventException: DestageBlocked | Major | **Yes** | Critical event; destage blocked. DUDL/availability risk. **Critical is correct.** |
| 19 | [WEKAPP-591224](https://wekaio.atlassian.net/browse/WEKAPP-591224) | UserDeletionFailed: Could not delete user – unknown username | Blocker | **Yes** | Auth/user management blocked. Per criterion 2 (feature blocked) → **Critical**. |
| 20 | [WEKAPP-591216](https://wekaio.atlassian.net/browse/WEKAPP-591216) | CriticalEventException: NfsClusterStatusInactiveEvent | Major | **Yes** | Critical event in NFS. **Critical is correct.** |
| 21 | [WEKAPP-591215](https://wekaio.atlassian.net/browse/WEKAPP-591215) | Mount: mount.nfs: NFS version or transport not supported | Major | **Consider** | NFS mount failure. If product protocol bug → Critical; if client/env config → **Major**. Re-check root cause. |
| 22 | [WEKAPP-591205](https://wekaio.atlassian.net/browse/WEKAPP-591205) | ExceptionNotRaised: Did not raise ProcessExecutionError as expected | Major | **No** | Test expectation (negative test). **Major** per Automation Bug guidance. |
| 23 | [WEKAPP-591007](https://wekaio.atlassian.net/browse/WEKAPP-591007) | Enable control over hosts batch removal / join interval | Major | **No** | Feature request / improvement. Not a bug. **Major** or lower. |
| 24 | [WEKAPP-590502](https://wekaio.atlassian.net/browse/WEKAPP-590502) | DisksNotFreedByAggressiveDieting: fill ratio > expected | Major | **Consider** | Test assertion on disk fill. If product dieting bug → Critical; if test threshold → **Major**. Re-check. |
| 25 | [WEKAPP-590187](https://wekaio.atlassian.net/browse/WEKAPP-590187) | while setup: Mount: Some containers did not become ready | Major | **No** | Phase = setup; containers not ready. Setup/env. **Major** per Automation Bug guidance. |
| 26 | [WEKAPP-590169](https://wekaio.atlassian.net/browse/WEKAPP-590169) | Backport Snap to GCS without access key/secret | Major | **No** | Backport/feature task. Not a bug. **Major** or lower. |
| 27 | [WEKAPP-588970](https://wekaio.atlassian.net/browse/WEKAPP-588970) | WekaCLIError: Some containers did not stop in time | Major | **No** | Test expectation (stop timeout). **Major** if test timing per Automation Bug guidance. |
| 28 | [WEKAPP-588580](https://wekaio.atlassian.net/browse/WEKAPP-588580) | PortTestFailed: weka-agent service failed to start | Major | **No** | Port test / agent start. Test/infra. **Major** per Automation Bug guidance. |
| 29 | [WEKAPP-588230](https://wekaio.atlassian.net/browse/WEKAPP-588230) | WekaCLIError: Some containers did not stop in time | Major | **No** | Same as 588970. Test timing. **Major**. |
| 30 | [WEKAPP-587554](https://wekaio.atlassian.net/browse/WEKAPP-587554) | Leadership Upgrade: Insufficient memory in cluster | Blocker | **Yes** | Upgrade blocked; insufficient memory. **Critical is correct.** |
| 31 | [WEKAPP-587247](https://wekaio.atlassian.net/browse/WEKAPP-587247) | ContainersSyncFailed: weka-agent isn't running | Major | **No** | Agent not running. Often env/lab; if product bug preventing agent start → Critical. Default **Major** until confirmed. |
| 32 | [WEKAPP-586478](https://wekaio.atlassian.net/browse/WEKAPP-586478) | CallFailed: stat64 ESTALE (mayhem snapshot path) | Major | **Consider** | ESTALE during mayhem. If product snapshot/FS semantics bug → Critical; if invalid scenario → **Major**. Re-check. |
| 33 | [WEKAPP-586327](https://wekaio.atlassian.net/browse/WEKAPP-586327) | WekaCLIError: Some containers did not stop in time | Major | **No** | Test expectation (stop timeout). **Major** if test timing. |
| 34 | [WEKAPP-586233](https://wekaio.atlassian.net/browse/WEKAPP-586233) | SnapshotPolicyInvalidMonthDayValue: day 29 invalid (must be 1–28) | Major | **Yes** | Product validation bug; snapshot policy rejects valid day 29. Affects schedule correctness. **Critical defensible** (scheduler broken for Feb 29). |
| 35 | [WEKAPP-584037](https://wekaio.atlassian.net/browse/WEKAPP-584037) | DidNotReachStatus: node did not reach UP, still DOWN | Major | **No** | Node stayed DOWN in test. If product bug → Critical; if test/env → **Major**. Default **Major** until root cause known. |
| 36 | [WEKAPP-583021](https://wekaio.atlassian.net/browse/WEKAPP-583021) | splice unit-test from weka/config modules | Minor | **No** | Unit test refactor. Not a bug. **Minor** or task. |
| 37 | [WEKAPP-582154](https://wekaio.atlassian.net/browse/WEKAPP-582154) | CriticalEventException: NodeUnreachable | Major | **Yes** | Critical event; node unreachable. **Critical is correct.** |
| 38 | [WEKAPP-581808](https://wekaio.atlassian.net/browse/WEKAPP-581808) | Cooperative failover serialize FS(Locks,Charters) state | Major | **No** | Feature/enhancement task. Not a bug. **Major** or lower. |
| 39 | [WEKAPP-581807](https://wekaio.atlassian.net/browse/WEKAPP-581807) | Cooperative failover serialize RAID state | Major | **No** | Feature/enhancement task. Not a bug. **Major** or lower. |
| 40 | [WEKAPP-581725](https://wekaio.atlassian.net/browse/WEKAPP-581725) | FileNotFoundError: No such file or directory | Major | **No** | Path not found in test. **Major** if test logic per Automation Bug guidance. |
| 41 | [WEKAPP-581666](https://wekaio.atlassian.net/browse/WEKAPP-581666) | wekanode SIGABRT at weka/reactor/ondemand_worker.d | Major | **Yes** | Product crash (SIGABRT). **Critical is correct.** |
| 42 | [WEKAPP-579565](https://wekaio.atlassian.net/browse/WEKAPP-579565) | Mayhem ESTALE – FSId/SnapshotId change while dir open | Major | **Consider** | ESTALE scenario; may be invalid test scenario. If product bug → Critical; if invalid scenario → **Major**. Re-check. |
| 43 | [WEKAPP-579018](https://wekaio.atlassian.net/browse/WEKAPP-579018) | RealUpgradeException: validation stage – No such file or address | Blocker | **Yes** | Upgrade failed at validation. **Critical is correct.** |
| 44 | [WEKAPP-577909](https://wekaio.atlassian.net/browse/WEKAPP-577909) | UnexpectedS0Death: Stress0 died on host | Major | **Consider** | Stress process died. If product caused it → Critical; if env/resource → **Major**. Re-check root cause. |
| 45 | [WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646) | ASSERT failed: FailedDisksTable[DiskId]=31 instead of 0 | Major | **Yes** | Product ASSERT in status_tables.d. **Critical is correct.** |
| 46 | [WEKAPP-568145](https://wekaio.atlassian.net/browse/WEKAPP-568145) | RealUpgradeException: buckets_list_statuses empty (after_upgrade) | Major | **Yes** | Upgrade failure; AssertionError in after_upgrade. **Critical is correct.** |
| 47 | [WEKAPP-560629](https://wekaio.atlassian.net/browse/WEKAPP-560629) | ExceptionNotRaised: Did not raise ProcessExecutionError as expected | Major | **No** | Test expectation (negative test). **Major** per Automation Bug guidance. |
| 48 | [WEKAPP-552659](https://wekaio.atlassian.net/browse/WEKAPP-552659) | FileDiffException: Data mismatch – driver reads FE netbufs after restarted FE poisons them | Critical | **Yes** | Data corruption / integrity bug. Per criterion 3 (DUDL) → **Critical is correct.** |

---

## Summary

| Category | Count |
|----------|-------|
| **Clearly Critical** (product crash, ASSERT, DUDL, upgrade blocked, CriticalEvent) | **19** |
| **Clearly Not Critical** (test/infra/env, feature request, test expectation) | **22** |
| **Consider / Re-check** (root cause needed) | **7** |

**Recommendation:** Raise severity to Critical for the 19 "Yes" tickets where product impact is clear. For the 7 "Consider" tickets, confirm root cause before changing severity.

---

## Detailed Explanations: Why Each Should Be Critical

The following maps each Critical ticket to the specific severity criteria from the Bug Severity Definition (Section 5.2) and explains the product impact.

---

### Criterion 1: Product Crash (SIGSEGV, SIGABRT, ASSERT)

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-591769](https://wekaio.atlassian.net/browse/WEKAPP-591769)** | **AssertionFailed in weka/network/lowlevel/mbuf.d** – The ASSERT occurs in `MBufPool.decref` (line 1941), which is core networking/memory management in wekanode. A failed assertion here indicates invalid state in the network buffer pool—possible use-after-free, double-free, or corruption. This can cause unplanned node crash, data path failure, or RDMA/network corruption. **Per criterion 1:** ASSERT in product code = product crash class. |
| **[WEKAPP-591655](https://wekaio.atlassian.net/browse/WEKAPP-591655)** | **wekanode.assert: unimprintFib called in stem mode** – The ASSERT in `weka/management/client.d` indicates a logic violation: a management client operation (`unimprintFib`) was invoked in the wrong mode (stem vs. non-stem). This implies state-machine or lifecycle bugs in management clients. **Per criterion 1:** Product ASSERT = unplanned crash/abort. |
| **[WEKAPP-591617](https://wekaio.atlassian.net/browse/WEKAPP-591617)** | **wekanode.assert in weka/fs/entrypoint/read.d** – The ASSERT failed during a filesystem read (Netbuf descriptor consistency). This is on the data path: reads can fail, return wrong data, or crash the node. **Per criterion 1:** ASSERT in read path = crash + potential data integrity risk (criterion 3). |
| **[WEKAPP-591591](https://wekaio.atlassian.net/browse/WEKAPP-591591)** | **CoreFoundException: ganesha** – Ganesha is the Weka NFS server component. A core dump in ganesha indicates unplanned process crash of a Tier-1 protocol server. NFS becomes unavailable; clients lose access. **Per criterion 1:** Core dump in product component = crash. **Per criterion 4:** Severe availability impact (NFS down). |
| **[WEKAPP-581666](https://wekaio.atlassian.net/browse/WEKAPP-581666)** | **wekanode SIGABRT at weka/reactor/ondemand_worker.d** – wekanode terminated with SIGABRT in the reactor’s on-demand worker. This is an unplanned crash of the main storage process. **Per criterion 1:** SIGABRT = product crash. Node down = severe availability impact. |
| **[WEKAPP-569646](https://wekaio.atlassian.net/browse/WEKAPP-569646)** | **ASSERT failed: FailedDisksTable[DiskId]=31 instead of 0** – The ASSERT in `weka/config/status_tables.d` shows inconsistency in the failed-disks tracking table. This suggests metadata/catalog corruption or incorrect state for disk status. **Per criterion 1:** Product ASSERT. **Per criterion 3:** Incorrect disk state can lead to wrong rebuild/placement decisions and DUDL risk. |

---

### Criterion 2: Feature / Deployment Blocked (Upgrade, Installation)

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-591707](https://wekaio.atlassian.net/browse/WEKAPP-591707)** | **ClientsNotUpgraded** – After `weka local upgrade` on each client, some clients never reach status UP in the new version. The upgrade flow is blocked: customers cannot complete the upgrade. **Per criterion 2:** Upgrade/deployment blocked. |
| **[WEKAPP-591590](https://wekaio.atlassian.net/browse/WEKAPP-591590)** | **RealUpgradeException: frontend0 timed out, connection refused** – During upgrade, frontend0 failed to initialize (connection refused to jrpc). The upgrade cannot proceed. **Per criterion 2:** Upgrade blocked. |
| **[WEKAPP-591290](https://wekaio.atlassian.net/browse/WEKAPP-591290)** | **UpgradeFailed: verify no rebuild failed, drives0 timed out** – Upgrade failed because the “verify no rebuild” step failed (system cannot guarantee all data is protected). The product correctly blocks upgrade when data safety cannot be verified. The bug is that verification fails incorrectly or times out, blocking a valid upgrade. **Per criterion 2:** Upgrade blocked. |
| **[WEKAPP-587554](https://wekaio.atlassian.net/browse/WEKAPP-587554)** | **Leadership Upgrade: Insufficient memory in cluster** – The upgrade is blocked due to insufficient memory in the cluster. Whether the cause is a product bug (wrong memory calculation) or a real capacity shortfall, the outcome is that upgrade cannot complete. **Per criterion 2:** Upgrade blocked. |
| **[WEKAPP-579018](https://wekaio.atlassian.net/browse/WEKAPP-579018)** | **RealUpgradeException: validation stage – No such file or address** – Upgrade failed during the validation stage (ProcessExecutionError, exit code 2). Validation is part of the upgrade flow; failure blocks the upgrade. **Per criterion 2:** Upgrade blocked. |
| **[WEKAPP-568145](https://wekaio.atlassian.net/browse/WEKAPP-568145)** | **RealUpgradeException: buckets_list_statuses empty (after_upgrade)** – Upgrade reached the after_upgrade stage but failed with AssertionError (buckets_list_statuses empty). Upgrade cannot be considered complete. **Per criterion 2:** Upgrade blocked. **Per criterion 1:** AssertionError indicates product defect. |

---

### Criterion 3: DUDL / Data Corruption Risk

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-591313](https://wekaio.atlassian.net/browse/WEKAPP-591313)** | **CriticalEventException: CacheFlushHanging** – Cache flush is hanging. Pending dirty data in cache cannot be flushed to backend. If the system cannot flush, data can be lost on failure or reboot. **Per criterion 3:** DUDL risk. **Per criterion 4:** Severe availability impact (writes can stall). |
| **[WEKAPP-591229](https://wekaio.atlassian.net/browse/WEKAPP-591229)** | **CriticalEventException: DestageBlocked** – Destage to backend is blocked. Similar to CacheFlushHanging: data cannot move from cache to durable storage. **Per criterion 3:** DUDL risk. **Per criterion 4:** Severe availability impact. |
| **[WEKAPP-552659](https://wekaio.atlassian.net/browse/WEKAPP-552659)** | **FileDiffException: Data mismatch – driver reads FE netbufs after restarted FE poisons them** – The driver reads netbufs that have been poisoned after a frontend restart. This causes data mismatch (read 0x00 vs expected 0xAD). **Per criterion 3:** Explicit data corruption. Reads return wrong data; customer data is at risk. |

---

### Criterion 4: Severe Availability Impact (Critical Events, Node Down)

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-591216](https://wekaio.atlassian.net/browse/WEKAPP-591216)** | **CriticalEventException: NfsClusterStatusInactiveEvent** – NFS cluster status is inactive. NFS service is down or degraded; clients cannot access NFS exports. **Per criterion 4:** Severe availability impact. |
| **[WEKAPP-582154](https://wekaio.atlassian.net/browse/WEKAPP-582154)** | **CriticalEventException: NodeUnreachable** – A backend node is unreachable. Cluster loses redundancy; if more nodes fail, data can become unavailable. **Per criterion 4:** Severe availability impact; can escalate to DUDL if additional failures occur. |

---

### Criterion 2 + 4: Feature Blocked + Availability

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-591224](https://wekaio.atlassian.net/browse/WEKAPP-591224)** | **UserDeletionFailed: Could not delete user – unknown username** – User deletion fails with “unknown username” even though the test expects the user to exist. Auth/user management is blocked; multi-tenant or user-lifecycle operations cannot complete. **Per criterion 2:** Feature (user management) blocked. **Per criterion 4:** Affects multi-tenancy and access control. |

---

### Criterion 3 + 4: Scheduler / Validation Bug (Affects Correctness)

| Ticket | Detailed Rationale |
|--------|--------------------|
| **[WEKAPP-586233](https://wekaio.atlassian.net/browse/WEKAPP-586233)** | **SnapshotPolicyInvalidMonthDayValue: day 29 invalid (must be 1–28)** – The snapshot policy rejects day 29 in monthly schedules. Feb 29 is valid in leap years; rejecting it is incorrect. Customers cannot create monthly snapshots on the 29th (or 30th/31st). **Per criterion 3:** Schedule correctness affects backup/retention. **Per criterion 2:** Feature (snapshot policy) incorrectly restricted. |