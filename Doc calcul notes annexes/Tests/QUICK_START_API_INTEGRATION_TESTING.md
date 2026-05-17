# Quick Start: API Integration Testing - Notes Annexes SYSCOHADA

## Task 30.2: Test API Integration with Claraverse Frontend

### Prerequisites

1. **Backend Running**
   ```bash
   python py_backend/main.py
   ```
   - Should start on `http://localhost:5000`
   - Check logs for "Notes Annexes SYSCOHADA API registered"

2. **Balance File Available**
   - File: `P000 -BALANCE DEMO N_N-1_N-2.xlsx`
   - Location: Project root directory
   - Size: Should be < 10 MB

3. **Frontend Running** (for manual tests)
   ```bash
   npm run dev
   ```
   - Should start on `http://localhost:5173`

---

## Automated Testing

### Run All Tests

```powershell
.\test-api-integration-notes-annexes.ps1
```

### Expected Output

```
═══════════════════════════════════════════════════════════════════════
  TEST API INTEGRATION - NOTES ANNEXES SYSCOHADA
  Task 30.2: Frontend Integration Testing
═══════════════════════════════════════════════════════════════════════

TEST 1: Backend Health Check
──────────────────────────────────────────────────────────────────────
Checking backend availability at: http://localhost:5000/api/notes_annexes/health
Service: Notes Annexes SYSCOHADA
Status: available
Version: 1.0.0
Backend is available and ready
✓ PASSED

TEST 2: Balance File Availability
──────────────────────────────────────────────────────────────────────
Checking for balance file: P000 -BALANCE DEMO N_N-1_N-2.xlsx
File found: P000 -BALANCE DEMO N_N-1_N-2.xlsx (2.5 MB)
✓ PASSED

...

═══════════════════════════════════════════════════════════════════════
  TEST SUMMARY
═══════════════════════════════════════════════════════════════════════

Total Tests:  12
Passed:       12
Failed:       0
Pass Rate:    100.0%

✓ ALL TESTS PASSED!

Task 30.2 Status: COMPLETE ✓
```

---

## Manual Testing

### Step 1: Test File Upload

1. Open browser to `http://localhost:5173`
2. Navigate to chat interface
3. Send message that triggers `Notes_Annexes` table
4. File dialog should open automatically
5. Select: `P000 -BALANCE DEMO N_N-1_N-2.xlsx`
6. Wait for processing (up to 30 seconds)

### Step 2: Verify Accordion Display

**Check:**
- ✓ 33 notes are displayed
- ✓ Each note has an icon and title
- ✓ Accordions expand/collapse on click
- ✓ "Tout Ouvrir" button works
- ✓ "Tout Fermer" button works
- ✓ Tables display with proper formatting
- ✓ Amounts are formatted with thousand separators

### Step 3: Test Error Handling

1. Trigger `Notes_Annexes` table again
2. Select an invalid file (e.g., `.txt` file)
3. Verify error message appears:
   - ✓ Clear error message
   - ✓ No crash or blank screen
   - ✓ User can retry

### Step 4: Verify Performance

**Measure:**
- ✓ Processing time < 30 seconds
- ✓ Coherence rate >= 95%
- ✓ All 33 notes calculated
- ✓ No errors in console

---

## Test Checklist

### Automated Tests (12 tests)

- [ ] Backend Health Check
- [ ] Balance File Availability
- [ ] API File Upload
- [ ] API Response Structure
- [ ] 33 Notes Calculation
- [ ] Notes Data Structure
- [ ] Coherence Rate Validation
- [ ] Performance Constraint
- [ ] Frontend Component Availability
- [ ] Auto-Trigger Script Availability
- [ ] Error Handling - Invalid File
- [ ] CSS Styling Availability

### Manual Tests

- [ ] File upload via frontend interface
- [ ] Accordion display verification
- [ ] Interactive accordion testing (expand/collapse)
- [ ] "Tout Ouvrir" button functionality
- [ ] "Tout Fermer" button functionality
- [ ] Error handling with invalid files
- [ ] Performance validation (< 30s)
- [ ] Coherence rate validation (>= 95%)
- [ ] Amount formatting verification
- [ ] Icon display for each note category

---

## Expected API Response

```json
{
  "success": true,
  "timestamp": "2026-04-29T10:30:00",
  "notes_calculees": 33,
  "notes_totales": 33,
  "taux_coherence": 98.5,
  "duree_calcul": 12.5,
  "notes": {
    "Note_3A": {
      "colonnes": [
        "Libellé",
        "Brut Ouverture",
        "Augmentations",
        "Diminutions",
        "Brut Clôture",
        "Amort Ouverture",
        "Dotations",
        "Reprises",
        "Amort Clôture",
        "VNC Ouverture",
        "VNC Clôture"
      ],
      "lignes": [
        ["Frais de recherche et de développement", 1500000, 500000, 0, 2000000, 300000, 200000, 0, 500000, 1200000, 1500000],
        ["Brevets, licences, logiciels", 800000, 200000, 0, 1000000, 400000, 100000, 0, 500000, 400000, 500000],
        ...
      ]
    },
    "Note_3B": { ... },
    ...
  },
  "statuts": {
    "Note_3A": "✓ Succès",
    "Note_3B": "✓ Succès",
    ...
  },
  "fichier_source": "P000 -BALANCE DEMO N_N-1_N-2.xlsx"
}
```

---

## Troubleshooting

### Backend Not Responding

**Symptoms:**
- TEST 1 fails
- Cannot connect to `http://localhost:5000`

**Solutions:**
1. Check backend is running: `python py_backend/main.py`
2. Verify port 5000 is not in use
3. Check firewall settings
4. Review backend logs for errors

### File Upload Fails

**Symptoms:**
- TEST 3 fails
- HTTP 400 or 500 error

**Solutions:**
1. Verify file format is `.xlsx` or `.xls`
2. Check file size < 10 MB
3. Ensure balance file has correct structure (3 worksheets: N, N-1, N-2)
4. Check file is not corrupted

### Processing Takes > 30 Seconds

**Symptoms:**
- TEST 8 fails
- Timeout errors

**Solutions:**
1. Check system resources (CPU, memory)
2. Close other applications
3. Verify balance file is not too large
4. Consider enabling parallel processing (if available)

### Accordions Not Displaying

**Symptoms:**
- Frontend shows blank or error
- No accordions visible

**Solutions:**
1. Check browser console for errors (F12)
2. Verify `NotesAnnexesAutoTrigger.js` is loaded
3. Check CSS file is loaded
4. Inspect network tab for API response
5. Clear browser cache and reload

### Invalid Coherence Rate

**Symptoms:**
- TEST 7 shows warning
- Coherence rate < 95%

**Solutions:**
1. Verify balance file has correct data
2. Check for missing accounts
3. Review balance coherence (N-1 closing = N opening)
4. Validate account mappings in `correspondances_syscohada.json`

---

## Success Criteria

Task 30.2 is **COMPLETE** when:

✓ All 12 automated tests pass
✓ File upload works via frontend
✓ 33 notes are displayed in accordions
✓ Accordions are interactive
✓ Error handling works correctly
✓ Performance < 30 seconds
✓ Coherence rate >= 95%

---

## Next Steps

After successful testing:

1. **Mark task 30.2 as COMPLETED** in `tasks.md`
2. **Proceed to task 30.3**: Performance validation
3. **Proceed to task 30.4**: Coherence validation
4. **Complete task 31**: Final checkpoint

---

## Quick Commands

```powershell
# Run automated tests
.\test-api-integration-notes-annexes.ps1

# Start backend
python py_backend/main.py

# Start frontend
npm run dev

# Check backend health
curl http://localhost:5000/api/notes_annexes/health

# View test results
cat test-results-api-integration-notes-annexes.json
```

---

## Contact & Support

For issues or questions:
- Review: `00_TASK_30_2_API_INTEGRATION_TESTING.txt`
- Check: `TROUBLESHOOTING.md` in Doc calcul notes annexes
- Review backend logs: `calcul_notes_annexes.log`
