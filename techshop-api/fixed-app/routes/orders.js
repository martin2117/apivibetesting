const express = require('express');
const { authenticate } = require('../middleware/auth');
const products = require('../data/products');

const router = express.Router();

const orderStore = {};

function getUserOrders(userId) {
  if (!orderStore[userId]) orderStore[userId] = [];
  return orderStore[userId];
}

/**
 * @openapi
 * /orders:
 *   get:
 *     summary: Get all orders for the current user
 *     tags: [Orders]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of orders
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Order'
 *       401:
 *         description: Unauthorized
 */
router.get('/', authenticate, (req, res) => {
  const orders = getUserOrders(req.user.id);
  res.json(orders);
});

/**
 * @openapi
 * /orders:
 *   post:
 *     summary: Place an order (checkout)
 *     tags: [Orders]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [items, shipping, payment]
 *             properties:
 *               items:
 *                 type: array
 *                 minItems: 1
 *                 items:
 *                   type: object
 *                   required: [productId, quantity]
 *                   properties:
 *                     productId:
 *                       type: integer
 *                       example: 1
 *                     quantity:
 *                       type: integer
 *                       minimum: 1
 *                       example: 2
 *               shipping:
 *                 type: object
 *                 required: [firstName, lastName, email, phone]
 *                 properties:
 *                   firstName:
 *                     type: string
 *                     example: Jane
 *                   lastName:
 *                     type: string
 *                     example: Doe
 *                   email:
 *                     type: string
 *                     format: email
 *                     example: jane@example.com
 *                   phone:
 *                     type: string
 *                     pattern: '^\d{10}$'
 *                     example: "0412345678"
 *               payment:
 *                 type: object
 *                 required: [cardNumber, expiryDate, cvv]
 *                 properties:
 *                   cardNumber:
 *                     type: string
 *                     pattern: '^\d{16}$'
 *                     example: "4111111111111111"
 *                   expiryDate:
 *                     type: string
 *                     pattern: '^(0[1-9]|1[0-2])\/\d{2}$'
 *                     description: MM/YY format — must not be in the past
 *                     example: "12/28"
 *                   cvv:
 *                     type: string
 *                     pattern: '^\d{3}$'
 *                     example: "123"
 *     responses:
 *       201:
 *         description: Order placed successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Order'
 *       400:
 *         description: Validation error
 *       401:
 *         description: Unauthorized
 */
// FIX B5: Expiry date is now validated against the current month/year
router.post('/', authenticate, (req, res) => {
  const { items, shipping, payment } = req.body;

  if (!items || !Array.isArray(items) || !items.length) {
    return res.status(400).json({ error: 'Order must contain at least one item' });
  }

  // Validate and populate each item in the order
  for (const item of items) {
    if (item.productId === undefined || item.quantity === undefined) {
      return res.status(400).json({ error: 'Each order item must contain productId and quantity' });
    }
    if (!Number.isInteger(item.productId)) {
      return res.status(400).json({ error: 'productId must be an integer' });
    }
    if (!Number.isInteger(item.quantity) || item.quantity < 1) {
      return res.status(400).json({ error: 'quantity must be an integer of at least 1' });
    }
    const product = products.find(p => p.id === item.productId);
    if (!product) {
      return res.status(400).json({ error: `Product with ID ${item.productId} not found` });
    }
    item.price = product.price;
    item.name = product.name;
  }

  if (!shipping || !shipping.firstName || !shipping.lastName || !shipping.email || !shipping.phone) {
    return res.status(400).json({ error: 'All shipping fields are required' });
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(shipping.email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }

  if (!/^\d{10}$/.test(shipping.phone)) {
    return res.status(400).json({ error: 'Phone must be 10 digits' });
  }

  if (!payment || !payment.cardNumber || !payment.expiryDate || !payment.cvv) {
    return res.status(400).json({ error: 'All payment fields are required' });
  }

  if (!/^\d{16}$/.test(payment.cardNumber)) {
    return res.status(400).json({ error: 'Card number must be 16 digits' });
  }

  if (!/^\d{3}$/.test(payment.cvv)) {
    return res.status(400).json({ error: 'CVV must be 3 digits' });
  }

  if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(payment.expiryDate)) {
    return res.status(400).json({ error: 'Expiry date must be MM/YY format' });
  }

  // FIX B5: Check that the card is not expired
  const [expMonth, expYear] = payment.expiryDate.split('/').map(Number);
  const now = new Date();
  const currentYear = now.getFullYear() % 100;
  const currentMonth = now.getMonth() + 1;

  if (expYear < currentYear || (expYear === currentYear && expMonth < currentMonth)) {
    return res.status(400).json({ error: 'Card has expired' });
  }

  const total = items.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0);

  const order = {
    id: `ORD-${Date.now()}`,
    userId: req.user.id,
    items,
    shipping,
    payment: { last4: payment.cardNumber.slice(-4), expiryDate: payment.expiryDate },
    total: parseFloat(total.toFixed(2)),
    status: 'confirmed',
    createdAt: new Date().toISOString()
  };

  getUserOrders(req.user.id).push(order);

  res.status(201).json(order);
});

module.exports = router;
