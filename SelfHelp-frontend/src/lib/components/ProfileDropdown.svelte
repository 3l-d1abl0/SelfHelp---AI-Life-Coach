<script lang="ts">
	import { signOut } from '@auth/sveltekit/client';
	import type { User } from '@auth/core/types';
	
	let { user }: { user: User } = $props();
	let isOpen = $state(false);
	let dropdownRef: HTMLDivElement;
	
	function toggleDropdown(): void {
		isOpen = !isOpen;
	}
	
	function closeDropdown(): void {
		isOpen = false;
	}
	
	function handleClickOutside(event: MouseEvent): void {
		if (dropdownRef && !dropdownRef.contains(event.target as Node)) {
			closeDropdown();
		}
	}
	
	$effect(() => {
		if (isOpen) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});
</script>

<div class="profile-dropdown" bind:this={dropdownRef}>
	<button class="profile-trigger" onclick={toggleDropdown}>
		<img src={user.image} alt={user.name} class="profile-avatar" />
	</button>
	
	{#if isOpen}
		<div class="dropdown">
			<div class="dropdown-header">
				<img src={user.image} alt={user.name} class="dropdown-avatar" />
				<div class="dropdown-info">
					<div class="dropdown-name">{user.name}</div>
					<div class="dropdown-email">{user.email}</div>
				</div>
			</div>
			
			<div class="dropdown-divider"></div>
			
			<a href="/meeting/new" class="dropdown-item" onclick={closeDropdown}>
				New Meet
			</a>

			<a href="/meetings" class="dropdown-item" onclick={closeDropdown}>
				My Meetings
			</a>
			
			<div class="dropdown-divider"></div>
			
			<button 
				class="dropdown-item logout-btn" 
				onclick={() => signOut({ callbackUrl: '/' })}
			>
				🚪 Logout
			</button>
		</div>
	{/if}
</div>

<style>
	.profile-dropdown {
		position: relative;
	}
	
	.profile-trigger {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
	}
	
	.dropdown {
		color: white;
		position: absolute;
		top: calc(100% + 0.5rem);
		right: 0;
		background: rgba(255, 255, 255, 0.15);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 10px;
		padding: 0.5rem 0;
		min-width: 280px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
		z-index: 1000;
		backdrop-filter: blur(10px);
	}
	
	.dropdown-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
	}
	
	.dropdown-avatar {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		border: 2px solid var(--primary);
	}
	
	.dropdown-info {
		flex: 1;
		min-width: 0;
	}
	
	.dropdown-name {
		font-weight: 600;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.dropdown-email {
		font-size: 0.875rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.dropdown-divider {
		height: 1px;
		background: rgba(255, 255, 255, 0.1);
		margin: 0.5rem 0;
	}
	
	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem 1rem;
		color: var(--text-light);
		text-decoration: none;
		background: none;
		border: none;
		cursor: pointer;
		transition: background 0.2s;
		font-size: 0.95rem;
	}
	
	.dropdown-item:hover {
		background: var(--light-gray);
	}
	
	.logout-btn {
		color: var(--error);
	}
	
	.logout-btn:hover {
		background: rgba(251, 133, 0, 0.1);
	}

    .profile-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 2px solid var(--primary);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .profile-avatar:hover {
        transform: scale(1.1);
        border-color: var(--accent);
    }
</style>