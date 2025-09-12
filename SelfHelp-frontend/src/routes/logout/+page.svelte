<script lang="ts">
    import { enhance } from '$app/forms';
</script>
 
<svelte:head>
	<title>Logout</title>
</svelte:head>



<div class="logout-page">
	<div class="container">
		<div class="logout-card card">
			<div class="logout-header">
				<h1>Are you sure you want to Logout ?</h1>
			</div>
				
			
			<form class="logout-form" method="POST" use:enhance>
				<button class="btn logout-btn" type="submit">Logout</button>
			</form>
			
		</div>
	</div>
</div>


<style>
	.logout-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.logout-card {
		max-width: 400px;
		width: 100%;
		text-align: center;
	}
	
    .logout-header{
        color: white;
    }

	.logout-header h1 {
		font-size: 1.5rem;
		margin-bottom: 2rem;
	}
	
	.logout-form {
		margin-bottom: 2rem;
	}

	.logout-btn{
		font-weight: 800;
		border-radius: 10px;
	}

</style>