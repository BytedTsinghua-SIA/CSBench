# tests/test_xv6_pgtbl.py
import re
import pytest
from gradelib import shell_script, assert_lines_match, check_time, assert_equal

PTE_PRINT = """page table 0x0000000087f6e000
 ..0: pte 0x0000000021fda801 pa 0x0000000087f6a000
 .. ..0: pte 0x0000000021fda401 pa 0x0000000087f69000
 .. .. ..0: pte 0x0000000021fdac1f pa 0x0000000087f6b000
 .. .. ..1: pte 0x0000000021fda00f pa 0x0000000087f68000
 .. .. ..2: pte 0x0000000021fd9c1f pa 0x0000000087f67000
 ..255: pte 0x0000000021fdb401 pa 0x0000000087f6d000
 .. ..511: pte 0x0000000021fdb001 pa 0x0000000087f6c000
 .. .. ..509: pte 0x0000000021fdd813 pa 0x0000000087f76000
 .. .. ..510: pte 0x0000000021fddc07 pa 0x0000000087f77000
 .. .. ..511: pte 0x0000000020001c0b pa 0x0000000080007000"""

VAL_RE   = r"(0x00000000[0-9a-f]+)"
INDENT_RE = r"\s*\.\.\s*"

@pytest.fixture(scope="module")
def pgtbl_output(r):
    r.run_qemu(shell_script(['pgtbltest']), timeout=300)
    return r.qemu.output

def test_pgtbl_ugetpid(pgtbl_output):
    assert_lines_match(pgtbl_output, r'^ugetpid_test: OK$')

def test_pgtbl_pgaccess(pgtbl_output):
    assert_lines_match(pgtbl_output, r'^pgaccess_test: OK$')

def test_pte_printout(r):
    r.run_qemu(shell_script(['echo hi']))
    r.match(r'^hi')

    p = re.compile(VAL_RE)
    d = re.compile(INDENT_RE)

    first = True
    for line in PTE_PRINT.splitlines():
        pattern = d.sub(lambda m: r"\s*\.\.\s*", line)
        pattern = p.sub(VAL_RE, pattern)
        r.match(r'^{}$'.format(pattern))

        if first:
            first = False
        else:
            matches = re.findall(r'^{}$'.format(pattern), r.qemu.output, re.MULTILINE)
            assert_equal(len(matches[0]), 2)
            pte_val = int(matches[0][0], 16)
            pa_val  = int(matches[0][1], 16)
            pa_from_pte = ((pte_val >> 10) << 12)
            assert_equal(pa_val, pa_from_pte)

def test_answers():
    from gradelib import check_answers
    check_answers("answers-pgtbl.txt")

def test_usertests_run(r):
    r.run_qemu(shell_script(['usertests']), timeout=300)

def test_usertests_all(r):
    r.match(r'^ALL TESTS PASSED$')

def test_time():
    check_time()