import './style.css'

// Deal Audit Validation Logic
class DealAuditor {
  constructor() {
    this.marketCPMRange = { min: 2.0, max: 15.0 };
    this.requiredKVPs = ['msft_refresh', 'brand_safety', 'inventory_type'];
    this.validDeviceTypes = ['mobile', 'desktop', 'tablet'];
    this.validCountryCodes = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'BR', 'MX'];
  }

  validateDeal(dealData) {
    const results = {};

    results.deal_status = this.checkDealStatus(dealData.status);
    results.buyer_seat = this.checkBuyerSeat(dealData.buyerSeatId);
    results.kvps = this.checkKVPs(dealData.kvps);
    results.targeting = this.checkTargeting(dealData.targeting);
    results.deal_list = this.checkDealList(dealData.dealListId);
    results.floor_price = this.checkFloorPrice(dealData.floorPrice);
    results.creative_audit = this.checkCreativeAudit(dealData.creativeApproved);
    results.inventory = this.checkInventory(dealData.inventoryStrength);
    results.historical = this.checkHistorical(dealData.historicalPerformance);

    const passed = Object.values(results).filter(r => r.passed).length;
    results.overall_outcome = this.calculateOutcome(passed, 9);

    return results;
  }

  checkDealStatus(status) {
    const passed = status === 'Active';
    return { passed, status: passed ? 'Active' : 'Inactive/Archived', issue: passed ? null : 'Deal is not active' };
  }

  checkBuyerSeat(buyerSeatId) {
    const passed = buyerSeatId && buyerSeatId.length > 0;
    return { passed, status: passed ? 'Present' : 'Missing', issue: passed ? null : 'Buyer seat ID missing' };
  }

  checkKVPs(kvps) {
    const missing = this.requiredKVPs.filter(k => !kvps || !kvps[k]);
    const passed = missing.length === 0;
    return { passed, status: passed ? 'Valid' : 'Invalid', issue: passed ? null : `Missing: ${missing.join(', ')}` };
  }

  checkTargeting(targeting) {
    const issues = [];
    if (targeting.geo && targeting.geo.length > 0) {
      const invalid = targeting.geo.filter(g => !this.validCountryCodes.includes(g));
      if (invalid.length > 0) issues.push(`Invalid countries: ${invalid.join(', ')}`);
    }
    if (targeting.devices && targeting.devices.length > 0) {
      const invalid = targeting.devices.filter(d => !this.validDeviceTypes.includes(d));
      if (invalid.length > 0) issues.push(`Invalid devices: ${invalid.join(', ')}`);
    }
    if (targeting.segments && targeting.segments.length > 5) {
      issues.push('Too many segments (restrictive)');
    }
    const passed = issues.length === 0;
    return { passed, status: passed ? 'All Pass' : (issues.length === 1 ? 'Minor Issue' : 'Multiple Issues'), issue: passed ? null : issues.join('; ') };
  }

  checkDealList(dealListId) {
    const passed = dealListId && dealListId.length > 0;
    return { passed, status: passed ? 'Approved' : 'Unapproved', issue: passed ? null : 'Deal List ID missing' };
  }

  checkFloorPrice(floorPrice) {
    if (floorPrice === null || floorPrice === '') {
      return { passed: false, status: 'Not Set', issue: 'Floor price not specified' };
    }
    const price = parseFloat(floorPrice);
    if (price < this.marketCPMRange.min) {
      return { passed: false, status: 'Too Low', issue: `Below market minimum ($${this.marketCPMRange.min})` };
    } else if (price > this.marketCPMRange.max) {
      return { passed: false, status: 'Too High', issue: `Above market maximum ($${this.marketCPMRange.max})` };
    }
    return { passed: true, status: 'Competitive', issue: null };
  }

  checkCreativeAudit(approved) {
    const passed = approved === true;
    return { passed, status: passed ? 'Approved' : 'Rejected/Pending', issue: passed ? null : 'Creative not approved' };
  }

  checkInventory(strength) {
    const validStrengths = ['Strong', 'Moderate'];
    const passed = validStrengths.includes(strength);
    return { passed, status: strength || 'Insufficient', issue: passed ? null : 'Insufficient inventory' };
  }

  checkHistorical(performance) {
    const validPerformances = ['Good', 'Mixed'];
    const passed = validPerformances.includes(performance);
    return { passed, status: performance || 'Unknown', issue: passed ? null : 'Poor historical performance' };
  }

  calculateOutcome(checksPassed, totalChecks) {
    const percentage = (checksPassed / totalChecks) * 100;
    if (percentage >= 90) {
      return { outcome: 'HIGH ✅', color: 'green', percentage: percentage.toFixed(1), recommendation: 'Deal ready for launch' };
    } else if (percentage >= 60) {
      return { outcome: 'MEDIUM ⚠️', color: 'yellow', percentage: percentage.toFixed(1), recommendation: 'Address flagged issues before launch' };
    } else {
      return { outcome: 'LOW ❌', color: 'red', percentage: percentage.toFixed(1), recommendation: 'Significant remediation required' };
    }
  }
}

const auditor = new DealAuditor();

// Form handling
document.querySelector('#app').innerHTML = `
  <div class="container">
    <header class="header">
      <h1>🟢 Deal ID Audit Tool</h1>
      <p>Comprehensive validation for programmatic deals</p>
    </header>

    <div class="audit-wrapper">
      <form id="auditForm" class="audit-form">
        <div class="form-section">
          <h2>Basic Information</h2>
          
          <div class="form-group">
            <label for="dealId">Deal ID</label>
            <input type="text" id="dealId" placeholder="e.g., D-1001" required>
          </div>

          <div class="form-group">
            <label for="status">Deal Status</label>
            <select id="status" required>
              <option value="">Select status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Archived">Archived</option>
            </select>
          </div>

          <div class="form-group">
            <label for="buyerSeatId">Buyer Seat ID</label>
            <input type="text" id="buyerSeatId" placeholder="e.g., BS-12345">
          </div>
        </div>

        <div class="form-section">
          <h2>Key-Value Pairs (KVPs)</h2>
          <div class="form-group">
            <label><input type="checkbox" name="kvp" value="msft_refresh" checked> msft_refresh</label>
          </div>
          <div class="form-group">
            <label><input type="checkbox" name="kvp" value="brand_safety" checked> brand_safety</label>
          </div>
          <div class="form-group">
            <label><input type="checkbox" name="kvp" value="inventory_type" checked> inventory_type</label>
          </div>
        </div>

        <div class="form-section">
          <h2>Targeting</h2>
          
          <div class="form-group">
            <label>Geo (Countries)</label>
            <div class="checkbox-group">
              <label><input type="checkbox" name="geo" value="US"> US</label>
              <label><input type="checkbox" name="geo" value="CA"> CA</label>
              <label><input type="checkbox" name="geo" value="GB"> GB</label>
              <label><input type="checkbox" name="geo" value="AU"> AU</label>
            </div>
          </div>

          <div class="form-group">
            <label>Device Types</label>
            <div class="checkbox-group">
              <label><input type="checkbox" name="device" value="mobile"> Mobile</label>
              <label><input type="checkbox" name="device" value="desktop"> Desktop</label>
              <label><input type="checkbox" name="device" value="tablet"> Tablet</label>
            </div>
          </div>

          <div class="form-group">
            <label for="segments">Audience Segments (comma-separated)</label>
            <input type="text" id="segments" placeholder="e.g., tech_enthusiasts, finance">
          </div>
        </div>

        <div class="form-section">
          <h2>Deal Configuration</h2>
          
          <div class="form-group">
            <label for="dealListId">Deal List ID</label>
            <input type="text" id="dealListId" placeholder="e.g., DL-9876">
          </div>

          <div class="form-group">
            <label for="floorPrice">Floor Price (CPM in $)</label>
            <input type="number" id="floorPrice" step="0.01" min="0" placeholder="e.g., 5.50">
          </div>

          <div class="form-group">
            <label><input type="checkbox" id="creativeApproved"> Creative Approved</label>
          </div>

          <div class="form-group">
            <label for="inventoryStrength">Inventory Strength</label>
            <select id="inventoryStrength">
              <option value="">Select strength</option>
              <option value="Strong">Strong</option>
              <option value="Moderate">Moderate</option>
              <option value="Weak">Weak</option>
            </select>
          </div>

          <div class="form-group">
            <label for="historicalPerformance">Historical Performance</label>
            <select id="historicalPerformance">
              <option value="">Select performance</option>
              <option value="Good">Good</option>
              <option value="Mixed">Mixed</option>
              <option value="Poor">Poor</option>
            </select>
          </div>
        </div>

        <button type="submit" class="btn-submit">Run Audit</button>
      </form>

      <div id="results" class="results-section hidden">
        <h2>Audit Results</h2>
        <div id="outcomeCard" class="outcome-card">
          <h3 id="outcomeText"></h3>
          <div id="progressBar" class="progress-bar">
            <div id="progressFill" class="progress-fill"></div>
          </div>
          <p id="percentageText"></p>
          <p id="recommendationText" class="recommendation"></p>
        </div>

        <div class="checks-grid">
          <div id="checksContainer"></div>
        </div>

        <button type="button" class="btn-reset" onclick="location.reload()">Run New Audit</button>
      </div>
    </div>
  </div>
`;

document.getElementById('auditForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Collect form data
  const dealData = {
    dealId: document.getElementById('dealId').value,
    status: document.getElementById('status').value,
    buyerSeatId: document.getElementById('buyerSeatId').value,
    kvps: {},
    targeting: {
      geo: Array.from(document.querySelectorAll('input[name="geo"]:checked')).map(el => el.value),
      devices: Array.from(document.querySelectorAll('input[name="device"]:checked')).map(el => el.value),
      segments: document.getElementById('segments').value.split(',').filter(s => s.trim()).map(s => s.trim())
    },
    dealListId: document.getElementById('dealListId').value,
    floorPrice: document.getElementById('floorPrice').value,
    creativeApproved: document.getElementById('creativeApproved').checked,
    inventoryStrength: document.getElementById('inventoryStrength').value,
    historicalPerformance: document.getElementById('historicalPerformance').value
  };

  // Build KVPs object
  document.querySelectorAll('input[name="kvp"]:checked').forEach(el => {
    dealData.kvps[el.value] = true;
  });

  // Run audit
  const results = auditor.validateDeal(dealData);

  // Display results
  displayResults(dealData, results);
});

function displayResults(dealData, results) {
  document.getElementById('auditForm').classList.add('hidden');
  document.getElementById('results').classList.remove('hidden');

  const outcome = results.overall_outcome;
  document.getElementById('outcomeText').textContent = `Deal ID ${dealData.dealId}: ${outcome.outcome}`;
  document.getElementById('outcomeText').style.color = outcome.color;

  const fillPercentage = parseFloat(outcome.percentage);
  document.getElementById('progressFill').style.width = fillPercentage + '%';
  document.getElementById('progressFill').style.backgroundColor = outcome.color;
  document.getElementById('percentageText').textContent = `${outcome.percentage}% Validation Complete`;
  document.getElementById('recommendationText').textContent = `📋 ${outcome.recommendation}`;

  // Display individual checks
  const checksHTML = `
        <div class="check-item ${results.deal_status.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.deal_status.passed ? '✅' : '❌'}</span>
            <span>Deal Status: ${results.deal_status.status}</span>
            ${results.deal_status.issue ? `<span class="issue">${results.deal_status.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.buyer_seat.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.buyer_seat.passed ? '✅' : '❌'}</span>
            <span>Buyer Seat ID: ${results.buyer_seat.status}</span>
            ${results.buyer_seat.issue ? `<span class="issue">${results.buyer_seat.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.kvps.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.kvps.passed ? '✅' : '❌'}</span>
            <span>KVPs: ${results.kvps.status}</span>
            ${results.kvps.issue ? `<span class="issue">${results.kvps.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.targeting.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.targeting.passed ? '✅' : '❌'}</span>
            <span>Targeting: ${results.targeting.status}</span>
            ${results.targeting.issue ? `<span class="issue">${results.targeting.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.deal_list.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.deal_list.passed ? '✅' : '❌'}</span>
            <span>Deal List ID: ${results.deal_list.status}</span>
            ${results.deal_list.issue ? `<span class="issue">${results.deal_list.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.floor_price.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.floor_price.passed ? '✅' : '❌'}</span>
            <span>Floor Price: ${results.floor_price.status}</span>
            ${results.floor_price.issue ? `<span class="issue">${results.floor_price.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.creative_audit.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.creative_audit.passed ? '✅' : '❌'}</span>
            <span>Creative Audit: ${results.creative_audit.status}</span>
            ${results.creative_audit.issue ? `<span class="issue">${results.creative_audit.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.inventory.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.inventory.passed ? '✅' : '❌'}</span>
            <span>Inventory: ${results.inventory.status}</span>
            ${results.inventory.issue ? `<span class="issue">${results.inventory.issue}</span>` : ''}
        </div>
        <div class="check-item ${results.historical.passed ? 'passed' : 'failed'}">
            <span class="check-icon">${results.historical.passed ? '✅' : '❌'}</span>
            <span>Historical Performance: ${results.historical.status}</span>
            ${results.historical.issue ? `<span class="issue">${results.historical.issue}</span>` : ''}
        </div>
    `;

  document.getElementById('checksContainer').innerHTML = checksHTML;
}
