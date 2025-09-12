<script>
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>{$page.status} : {$page.error.message}</title>
</svelte:head>

<div class="error-page">
	<div class="container">
		<div class="error-card card">
			<div class="error-animation">
				<div class="glitch" data-text="{$page.status}">{$page.status}</div>
			</div>
			
			<h1>{$page.error.message}</h1>
			<p>The page you're looking for doesn't exist or has been moved.</p>
			
			<div class="error-actions">
				<a href="/" class="btn btn-primary">
					Go Home
				</a>
			</div>
		</div>
	</div>
</div>

<style>
	.error-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.error-card {
		max-width: 500px;
		text-align: center;
	}
	
	.error-animation {
		margin-bottom: 2rem;
	}
	
	.glitch {
		font-size: 6rem;
		font-weight: 900;
		color: var(--primary);
		position: relative;
		display: inline-block;
	}
	
	.glitch::before,
	.glitch::after {
		content: attr(data-text);
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
	}
	
	.glitch::before {
		animation: glitch-anim 2s infinite linear alternate-reverse;
		color: red;
		z-index: -1;
	}
	
	.glitch::after {
		animation: glitch-anim2 1s infinite linear alternate-reverse;
		color: orange;
		z-index: -2;
	}
	
	@keyframes glitch-anim {
		0% { clip: rect(42px, 9999px, 44px, 0); }
		5% { clip: rect(12px, 9999px, 59px, 0); }
		10% { clip: rect(48px, 9999px, 29px, 0); }
		15% { clip: rect(42px, 9999px, 73px, 0); }
		20% { clip: rect(63px, 9999px, 27px, 0); }
		25% { clip: rect(34px, 9999px, 55px, 0); }
		30% { clip: rect(86px, 9999px, 73px, 0); }
		35% { clip: rect(20px, 9999px, 20px, 0); }
		40% { clip: rect(26px, 9999px, 60px, 0); }
		45% { clip: rect(25px, 9999px, 66px, 0); }
		50% { clip: rect(57px, 9999px, 98px, 0); }
		55% { clip: rect(5px, 9999px, 46px, 0); }
		60% { clip: rect(82px, 9999px, 31px, 0); }
		65% { clip: rect(54px, 9999px, 27px, 0); }
		70% { clip: rect(28px, 9999px, 99px, 0); }
		75% { clip: rect(45px, 9999px, 69px, 0); }
		80% { clip: rect(23px, 9999px, 85px, 0); }
		85% { clip: rect(54px, 9999px, 84px, 0); }
		90% { clip: rect(45px, 9999px, 47px, 0); }
		95% { clip: rect(37px, 9999px, 20px, 0); }
		100% { clip: rect(4px, 9999px, 91px, 0); }
	}
	
	@keyframes glitch-anim2 {
		0% { clip: rect(65px, 9999px, 100px, 0); }
		5% { clip: rect(52px, 9999px, 74px, 0); }
		10% { clip: rect(79px, 9999px, 85px, 0); }
		15% { clip: rect(75px, 9999px, 5px, 0); }
		20% { clip: rect(67px, 9999px, 61px, 0); }
		25% { clip: rect(14px, 9999px, 79px, 0); }
		30% { clip: rect(1px, 9999px, 66px, 0); }
		35% { clip: rect(86px, 9999px, 30px, 0); }
		40% { clip: rect(23px, 9999px, 98px, 0); }
		45% { clip: rect(85px, 9999px, 72px, 0); }
		50% { clip: rect(71px, 9999px, 75px, 0); }
		55% { clip: rect(2px, 9999px, 48px, 0); }
		60% { clip: rect(30px, 9999px, 16px, 0); }
		65% { clip: rect(59px, 9999px, 50px, 0); }
		70% { clip: rect(41px, 9999px, 62px, 0); }
		75% { clip: rect(2px, 9999px, 82px, 0); }
		80% { clip: rect(47px, 9999px, 73px, 0); }
		85% { clip: rect(3px, 9999px, 27px, 0); }
		90% { clip: rect(26px, 9999px, 55px, 0); }
		95% { clip: rect(75px, 9999px, 96px, 0); }
		100% { clip: rect(60px, 9999px, 70px, 0); }
	}
	
	.error-card h1 {
		font-size: 2rem;
		margin-bottom: 1rem;
		color: black;
	}
	
	.error-card p {
		color: black;
		margin-bottom: 2rem;
		line-height: 1.6;
	}
	
	.error-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

    .btn-primary{
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        background: linear-gradient(90deg, #621e40 0%, #792828 100%);
		color: white;
        font-weight: 800;
    }

    .btn-primary:hover{
		transform: translateY(-1px) scale(1.05);
        box-shadow: 0 20px 50px rgba(15, 15, 15, 0.5);
        background: linear-gradient(135deg, #321F01 0%, #7F1204 50%, #CB0407 100%);
        text-decoration: none;
        
    }

</style>
