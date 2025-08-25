import { Redis } from 'ioredis';
import { Directus } from '@directus/sdk';
import { promises as fs } from 'fs';

// Mock Graphiti for demonstration purposes
class MockGraphiti {
  constructor(options: { url: string }) {
    console.log(`MockGraphiti initialized with URL: ${options.url}`);
  }

  async query(cypher: string, params?: any): Promise<any[]> {
    console.log(`MockGraphiti query: ${cypher}, params: ${JSON.stringify(params)}`);
    // Simulate a source of truth query result
    if (cypher.includes('source_of_truth')) {
      return [{ path: 'memU/01_MEMORY_CORE', priority: 1 }];
    }
    // Simulate memory grounding results
    if (cypher.includes('MATCH (m:Memory)')) {
      return [
        { m: { content: 'Memory context 1: This is a test memory entry.' } },
        { m: { content: 'Memory context 2: Another relevant piece of information.' } }
      ];
    }
    return [];
  }
}

// Mock FastMCP for demonstration purposes
class MockFastMCP {
  async registerTools(tools: any[]) {
    console.log(`MockFastMCP: Registered ${tools.length} tools.`);
  }
}

// Mock prompt-optimizer for demonstration purposes
async function optimize(prompt: string): Promise<string> {
  console.log(`Mock optimize function called with prompt: ${prompt}`);
  return `Optimized: ${prompt}`;
}

class IZAKernel {
  private redis: Redis;
  private directus: Directus<any>;
  private graphiti: MockGraphiti;
  private mcp: MockFastMCP;
  private sourceOfTruth: string | undefined;

  constructor() {
    this.redis = new Redis();
    this.directus = new Directus('http://localhost:8055'); // Assuming Directus runs on 8055
    this.graphiti = new MockGraphiti({ url: 'http://localhost:8001' }); // Assuming Graphiti runs on 8001
    this.mcp = new MockFastMCP();
  }

  async boot() {
    console.log('🧠 IZA OS Kernel booting...');

    // 1. Assert Source of Truth
    await this.assertSourceOfTruth();

    // 2. Start message bus
    console.log('Subscribing to Redis channels...');
    this.redis.subscribe('task:create', 'agent:spawn', 'memory:write', (err, count) => {
      if (err) {
        console.error('Failed to subscribe:', err);
      } else {
        console.log(`Subscribed to ${count} channels.`);
      }
    });

    // 3. Register all MCP tools
    await this.mcp.registerTools(this.loadTools());

    // 4. Start prompt router
    this.startPromptRouter();

    // 5. Announce readiness
    await this.redis.publish('system:ready', 'IZA OS Kernel online');
    console.log('IZA OS Kernel online and ready.');
  }

  async assertSourceOfTruth() {
    console.log('Asserting Source of Truth...');
    const truth = await this.graphiti.query(`
      MATCH (n:Node {role: 'source_of_truth'})
      RETURN n.path, n.priority
      ORDER BY n.priority DESC
      LIMIT 1
    `);

    if (!truth || truth.length === 0 || !truth[0]) {
      throw new Error('No Source of Truth defined. System cannot operate.');
    }

    this.sourceOfTruth = truth[0].path; // e.g., "memU/01_MEMORY_CORE"
    console.log(`Source of Truth asserted: ${this.sourceOfTruth}`);
  }

  startPromptRouter() {
    console.log('Starting prompt router...');
    this.redis.on('message', async (channel, message) => {
      if (channel === 'user:input') {
        console.log(`Received user input: ${message}`);
        try {
          const { id, prompt } = JSON.parse(message);
          const validated = await this.validatePrompt(prompt);
          const routed = await this.routePrompt(validated);
          await this.redis.publish('task:router:out', JSON.stringify(routed));
          console.log(`Routed prompt for ID ${id}: ${JSON.stringify(routed)}`);
        } catch (error) {
          console.error('Error processing user input:', error);
        }
      }
    });
  }

  async validatePrompt(prompt: string) {
    console.log(`Validating prompt: ${prompt}`);
    // Use prompt-optimizer + GPT Super Prompting
    const optimized = await optimize(prompt);
    const grounded = await this.groundInMemory(optimized);
    return this.addExecutionGuardrails(grounded);
  }

  async groundInMemory(prompt: string) {
    console.log(`Grounding prompt in memory: ${prompt}`);
    const results = await this.graphiti.query(`
      MATCH (m:Memory) WHERE m.content CONTAINS $prompt
      RETURN m LIMIT 3
    `, { prompt });

    const context = results.map(r => r.m.content).join('\n');
    return `${prompt}\n\nCONTEXT FROM MEMORY:\n${context}`; // Use \n for newlines
  }

  async addExecutionGuardrails(prompt: string) {
    console.log('Adding execution guardrails...');
    // Example of fs.exists() check (conceptual, as actual path validation would be more complex)
    const dummyPath = '/tmp/some/dummy/path.txt'; // Placeholder for a path that might be checked
    let pathExists = false;
    try {
      await fs.access(dummyPath);
      pathExists = true;
    } catch (e) {
      pathExists = false;
    }
    console.log(`Dummy path ${dummyPath} exists: ${pathExists}`);

    return `
${prompt}

## 🛑 EXECUTION RULES
- NEVER assume paths
- ALWAYS verify with fs.exists() (e.g., checked ${dummyPath}: ${pathExists})
- If uncertain: return [NEEDS_VERIFICATION]
- Cite source: # Source: /trusted/path.md
    `;
  }

  loadTools() {
    // Register all tools from MCP registry
    // e.g., backtest, deploy, memory write
    console.log('Loading MCP tools...');
    return [
      { name: 'backtest', description: 'Runs a backtest' },
      { name: 'deploy', description: 'Deploys a service' },
      { name: 'memoryWrite', description: 'Writes to memory' }
    ];
  }
}

const kernel = new IZAKernel();
kernel.boot().catch(error => {
  console.error('IZA OS Kernel failed to boot:', error);
  process.exit(1);
});
