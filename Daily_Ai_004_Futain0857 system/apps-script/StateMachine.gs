/**
 * Canonical Uppercase Status Definitions & State Machine Validation
 */

var CANONICAL_STATUS = {
  CONTAINER: {
    AVAILABLE: 'AVAILABLE',
    RESERVED: 'RESERVED',
    RENTED: 'RENTED',
    INSPECTION: 'INSPECTION',
    MAINTENANCE: 'MAINTENANCE',
    BLOCKED: 'BLOCKED',
    RETIRED: 'RETIRED'
  },
  CONTRACT: {
    DRAFT: 'DRAFT',
    ACTIVE: 'ACTIVE',
    ENDING: 'ENDING',
    ENDED: 'ENDED',
    CANCELLED: 'CANCELLED'
  },
  INVOICE: {
    UNPAID: 'UNPAID',
    PARTIAL: 'PARTIAL',
    PAID: 'PAID',
    VOID: 'VOID'
  },
  PAYMENT: {
    CONFIRMED: 'CONFIRMED',
    VOID: 'VOID',
    REFUNDED: 'REFUNDED'
  }
};

/**
 * Valid transitions for entities
 */
var ALLOWED_TRANSITIONS = {
  container: {
    'AVAILABLE': ['RESERVED', 'RENTED', 'MAINTENANCE', 'BLOCKED', 'RETIRED'],
    'RESERVED': ['RENTED', 'AVAILABLE', 'CANCELLED'],
    'RENTED': ['INSPECTION', 'ENDING'], // Direct transition RENTED -> AVAILABLE is ILLEGAL!
    'INSPECTION': ['AVAILABLE', 'MAINTENANCE'],
    'MAINTENANCE': ['AVAILABLE', 'RETIRED'],
    'BLOCKED': ['AVAILABLE'],
    'RETIRED': []
  },
  contract: {
    'DRAFT': ['ACTIVE', 'CANCELLED'],
    'ACTIVE': ['ENDING', 'ENDED', 'CANCELLED'],
    'ENDING': ['ENDED', 'CANCELLED'],
    'ENDED': [], // Transition ENDED -> ACTIVE is ILLEGAL!
    'CANCELLED': []
  },
  invoice: {
    'UNPAID': ['PARTIAL', 'PAID', 'VOID'],
    'PARTIAL': ['PAID', 'VOID'],
    'PAID': ['VOID'], // Transition PAID -> UNPAID is ILLEGAL!
    'VOID': []
  },
  payment: {
    'CONFIRMED': ['VOID', 'REFUNDED'],
    'VOID': [], // Transition VOID -> CONFIRMED is ILLEGAL!
    'REFUNDED': []
  },
  customer: {
    'ACTIVE': ['INACTIVE'],
    'INACTIVE': ['ACTIVE']
  }
};

/**
 * Validate status transition according to state machine whitelist
 */
function validateStatusTransition(entityType, currentStatus, newStatus) {
  if (!currentStatus || !newStatus) return;
  var currentUpper = currentStatus.toString().toUpperCase();
  var newUpper = newStatus.toString().toUpperCase();

  if (currentUpper === newUpper) return; // Same status, no-op

  var entityRules = ALLOWED_TRANSITIONS[entityType];
  if (!entityRules) {
    throw new AppError('INVALID_STATE', '未知的實體型別: ' + entityType);
  }

  var allowedNext = entityRules[currentUpper];
  if (!allowedNext || allowedNext.indexOf(newUpper) === -1) {
    throw new AppError(
      'INVALID_STATE',
      '非法狀態轉變 (' + entityType + '): 禁止由 ' + currentUpper + ' 直接變更為 ' + newUpper
    );
  }
}

/**
 * Normalize status string to uppercase canonical form
 */
function normalizeStatusValue(statusStr, defaultStatus) {
  if (!statusStr || statusStr.toString().trim() === '') {
    return defaultStatus || '';
  }
  return statusStr.toString().trim().toUpperCase();
}

function getStateMachineEntityType(tableName) {
  var map = {
    customers: "customer",
    containers: "container",
    contracts: "contract",
    invoices: "invoice",
    payments: "payment"
  };
  return map[tableName] || null;
}
