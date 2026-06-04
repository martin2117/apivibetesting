const express = require('express');
const products = require('../data/products');

const router = express.Router();

/**
 * @openapi
 * /products:
 *   get:
 *     summary: Get all products
 *     tags: [Products]
 *     parameters:
 *       - in: query
 *         name: category
 *         schema:
 *           type: string
 *         description: Filter by category (computers, audio, accessories, peripherals)
 *     responses:
 *       200:
 *         description: List of products
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Product'
 */
router.get('/', (req, res) => {
  if (req.originalUrl.split('?')[0].endsWith('/')) {
    return res.status(404).json({ error: 'Product ID not specified' });
  }

  const { category } = req.query;

  let result = products;
  if (category) {
    result = products.filter(p => p.category === category);
  }

  res.json(result.map(p => ({ ...p, inStock: p.stock > 0 })));
});

router.all('/', (req, res) => {
  res.setHeader('Allow', 'GET');
  res.status(405).json({ error: `Method ${req.method} not allowed on /products` });
});

/**
 * @openapi
 * /products/{id}:
 *   get:
 *     summary: Get a single product by ID
 *     tags: [Products]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: Product ID
 *     responses:
 *       200:
 *         description: Product found
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Product'
 *       404:
 *         description: Product not found
 */
// FIX B3: Explicit 404 returned when product does not exist
router.get('/:id', (req, res) => {
  const product = products.find(p => p.id === parseInt(req.params.id));

  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }

  res.json({ ...product, inStock: product.stock > 0 });
});

module.exports = router;
