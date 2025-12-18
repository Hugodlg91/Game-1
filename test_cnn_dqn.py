"""
Quick test script to verify CNN + Double DQN implementation.

Trains for 100 episodes and compares with expected performance.
"""
from dqn_agent import DQNAgent, train_dqn
import time

print("=" * 70)
print("CNN + DOUBLE DQN - QUICK TEST")
print("=" * 70)
print()

# Test 1: Agent creation
print("Test 1: Creating CNN agent...")
agent_cnn = DQNAgent(use_cnn=True)
print(f"✅ CNN Agent created")
print(f"   Parameters: {sum(p.numel() for p in agent_cnn.policy_net.parameters()):,}")
print()

# Test 2: Legacy MLP for comparison
print("Test 2: Creating legacy MLP agent...")
agent_mlp = DQNAgent(use_cnn=False)
print(f"✅ MLP Agent created")
print(f"   Parameters: {sum(p.numel() for p in agent_mlp.policy_net.parameters()):,}")
print()

# Test 3: Quick training (100 episodes)
print("Test 3: Training CNN for 100 episodes...")
print("This will take ~2-5 minutes on GPU")
print()

start_time = time.time()

# Import is here to avoid conflicts
from game_2048 import Game2048
from dqn_agent import ACTIONS, calculate_reward

episode_scores = []

for episode in range(100):
    game = Game2048()
    state = agent_cnn.preprocess_state(game.board)
    episode_score = 0
    steps = 0
    
    while game.has_moves_available() and steps < 10000:
        # Select action
        action_idx = agent_cnn.select_action(state)
        action = ACTIONS[action_idx]
        
        # Execute
        old_board = [row[:] for row in game.board]
        moved = game.move(action)
        game_over = not game.has_moves_available()
        
        # Reward
        reward = calculate_reward(old_board, game.board, moved, game_over)
        next_state = agent_cnn.preprocess_state(game.board)
        
        # Store
        agent_cnn.memory.push(state, action_idx, reward, next_state, game_over)
        
        # Optimize
        if len(agent_cnn.memory) >= 64:
            agent_cnn.optimize_model(batch_size=64)
        
        state = next_state
        episode_score = game.score
        steps += 1
    
    episode_scores.append(episode_score)
    agent_cnn.decay_epsilon()
    
    if (episode + 1) % 10 == 0:
        avg_score = sum(episode_scores[-10:]) / 10
        print(f"Episode {episode + 1}/100 | Avg Score: {avg_score:.1f} | ε: {agent_cnn.epsilon:.3f}")

elapsed = time.time() - start_time

print()
print("=" * 70)
print("TEST RESULTS")
print("=" * 70)
print(f"Training time: {elapsed:.1f}s ({elapsed/100:.2f}s per episode)")
print(f"Average score (last 50): {sum(episode_scores[-50:])/50:.1f}")
print(f"Best score: {max(episode_scores)}")
print(f"Final epsilon: {agent_cnn.epsilon:.3f}")
print()

# Expected ranges
avg_score = sum(episode_scores[-50:])/50
if avg_score > 300:
    print("✅ CNN is learning well! (Score > 300)")
elif avg_score > 200:
    print("⚠️  CNN is learning but could be better (Score 200-300)")
else:
    print("❌ CNN might have issues (Score < 200)")

print()
print("💡 For full performance, train for 3000-5000 episodes")
print("   Expected final score: 5000-10000")
print()
