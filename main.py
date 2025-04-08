"""
Main Entry Point for DQN Ice Hockey Project

This module serves as the central entry point for the project, providing a unified
interface for training, evaluation, and visualization. It uses argparse to create a
user-friendly command-line interface for all project functionality.

Usage:
    python main.py train [options]      - Train a new model
    python main.py evaluate [options]   - Evaluate a trained model
    python main.py compare [options]    - Compare multiple models
    python main.py visualize [options]  - Visualize training results
"""

import argparse
import os
import sys
import torch
import config
import utils
from train import train
from evaluate import evaluate_model, compare_models, plot_evaluation_results

def main():
    """
    Parse command-line arguments and execute the requested command.
    """
    parser = argparse.ArgumentParser(
        description="DQN for Atari Ice Hockey",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # === Train command ===
    train_parser = subparsers.add_parser("train", help="Train a DQN agent")
    train_parser.add_argument("--output_dir", type=str, default=None, help="Directory to save outputs")
    train_parser.add_argument("--episodes", type=int, default=config.TRAINING_EPISODES, help="Number of episodes to train")
    train_parser.add_argument("--learning_starts", type=int, default=config.LEARNING_STARTS, help="Steps before training begins")
    train_parser.add_argument("--render", action="store_true", help="Render training episodes")
    train_parser.add_argument("--gpu", action="store_true", help="Force GPU usage")
    train_parser.add_argument("--cpu", action="store_true", help="Force CPU usage")
    train_parser.add_argument("--model", type=str, default=None, help="Path to a pre-trained model to continue training")
    
    # === Evaluate command ===
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a trained model")
    eval_parser.add_argument("model", type=str, help="Path to the model file (.pth)")
    eval_parser.add_argument("--episodes", type=int, default=10, help="Number of episodes")
    eval_parser.add_argument("--render", action="store_true", help="Render environment")
    eval_parser.add_argument("--video", action="store_true", help="Record video")
    eval_parser.add_argument("--gpu", action="store_true", help="Force GPU usage")
    eval_parser.add_argument("--cpu", action="store_true", help="Force CPU usage")
    
    # === Compare command ===
    compare_parser = subparsers.add_parser("compare", help="Compare multiple models")
    compare_parser.add_argument("models", type=str, nargs="+", help="Paths to model files (.pth)")
    compare_parser.add_argument("--episodes", type=int, default=10, help="Number of episodes per model")
    compare_parser.add_argument("--gpu", action="store_true", help="Force GPU usage")
    compare_parser.add_argument("--cpu", action="store_true", help="Force CPU usage")
    
    # === Visualize command ===
    viz_parser = subparsers.add_parser("visualize", help="Visualize results")
    viz_parser.add_argument("results", type=str, help="Path to evaluation results file (.pkl)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, show help
    if args.command is None:
        parser.print_help()
        return
    
    # Determine device (CPU/GPU)
    device = determine_device(args)
    
    # Execute the appropriate command
    if args.command == "train":
        # Override config if specified through command line
        if args.episodes != config.TRAINING_EPISODES:
            print(f"Overriding training episodes from {config.TRAINING_EPISODES} to {args.episodes}")
            config.TRAINING_EPISODES = args.episodes
            
        if args.learning_starts != config.LEARNING_STARTS:
            print(f"Overriding learning start threshold from {config.LEARNING_STARTS} to {args.learning_starts}")
            config.LEARNING_STARTS = args.learning_starts
        
        # Run training
        trained_agent, stats = train(
            device=device,
            render_training=args.render,
            output_dir=args.output_dir
        )
        
        print("Training complete!")
        
    elif args.command == "evaluate":
        # Run evaluation
        results = evaluate_model(
            model_path=args.model,
            num_episodes=args.episodes,
            render=args.render,
            record_video=args.video,
            device=device
        )
        
        if results is None:
            print("Evaluation failed.")
        
    elif args.command == "compare":
        # Run model comparison
        compare_models(
            model_paths=args.models,
            num_episodes=args.episodes,
            device=device
        )
        
    elif args.command == "visualize":
        # Plot evaluation results
        plot_evaluation_results(args.results)
        
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


def determine_device(args):
    """
    Determine which device (CPU/GPU) to use based on command-line arguments
    and available hardware.
    
    Args:
        args: Command-line arguments
        
    Returns:
        torch.device: Device to use
    """
    if hasattr(args, "gpu") and hasattr(args, "cpu"):
        if args.gpu and args.cpu:
            print("Error: Cannot specify both --gpu and --cpu")
            sys.exit(1)
        elif args.gpu:
            if torch.cuda.is_available():
                device = torch.device("cuda")
                print(f"Using CUDA GPU: {torch.cuda.get_device_name()}")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = torch.device("mps")
                print("Using Apple Silicon GPU (MPS)")
            else:
                print("Warning: GPU requested but no compatible GPU found, using CPU instead")
                device = torch.device("cpu")
        elif args.cpu:
            device = torch.device("cpu")
            print("Forcing CPU usage as requested")
        else:
            device = utils.get_device()  # Auto-detect
    else:
        device = utils.get_device()  # Auto-detect
    
    return device


def display_project_info():
    """
    Display basic information about the project on startup.
    """
    print("\n" + "="*70)
    print(" "*20 + "DQN for Atari Ice Hockey" + " "*20)
    print(" "*15 + "Reinforcement Learning Project" + " "*15)
    print("="*70)
    
    # System information
    system_info = utils.get_system_info()
    print(f"Running on: {system_info['os']} with PyTorch {system_info['torch_version']}")
    
    if system_info.get('cuda_available', False):
        print(f"GPU: {system_info.get('gpu_name', 'Unknown')} "
              f"({system_info.get('gpu_memory_gb', 'Unknown')} GB)")
    elif system_info.get('mps_available', False):
        print("GPU: Apple Silicon (Metal)")
    else:
        print("No GPU detected, using CPU only")
    
    print("\nAvailable commands:")
    print("  train     - Train a DQN agent")
    print("  evaluate  - Evaluate a trained model")
    print("  compare   - Compare multiple models")
    print("  visualize - Visualize training results")
    print("\nFor more information on a specific command, run: python main.py <command> --help")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Display project information on startup
    display_project_info()
    
    # Run main function
    main()

